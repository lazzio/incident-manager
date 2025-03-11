from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from incidents.forms import IncidentForm, IncidentUpdateForm, Comment, CommentForm, LinkFormSet
from incidents.models import Incident, Severity, IncidentFile
from django.db import transaction


def validate_forms(request, form, link_formset) -> bool:
    """
    Validates the main form and link formset, displaying appropriate error messages.
    This function checks if both the main incident form and the associated link formset
    are valid. If any form contains errors, it prints detailed error information to the
    console and displays user-friendly error messages using Django's messages framework.
    Args:
        request (HttpRequest): The Django HTTP request object used for adding messages
        form (ModelForm): The main incident form to validate
        link_formset (BaseFormSet): The formset for incident-related links to validate
    Returns:
        bool: True if both forms are valid, False otherwise
    """
    """Helper function to validate forms and display error messages"""
    is_valid = True
    
    if not form.is_valid():
        print("Form errors:", form.errors.as_data())
        for field, errors in form.errors.items():
            print(f"Field {field} errors: {errors}")
        messages.error(request, "Le formulaire contient des erreurs. Veuillez les corriger.")
        is_valid = False
    
    if not link_formset.is_valid():
        print("Linkformset errors:", link_formset.errors)
        messages.error(request, "Le formulaire de liens contient des erreurs.")
        is_valid = False
        
    return is_valid


@login_required
def add_incident_update(request: object, pk: int) -> object:
    """
    Add an update to an existing incident.
    This view function handles POST requests to add updates to an incident. It fetches the
    incident using the provided primary key, validates the submitted form data, and saves
    the update with the incident reference and current user as the updater.
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the incident to update.
    Returns:
        HttpResponseRedirect: Redirects to the incident detail page after processing.
    Raises:
        Http404: If no incident with the given primary key exists.
    """
    incident = get_object_or_404(Incident, pk=pk)
    
    if request.method == 'POST':
        form = IncidentUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.incident = incident
            update.updated_by = request.user
            update.save()
    
    return redirect('incident_detail', pk=pk)


@login_required
def add_comment(request: object, pk: int) -> object:
    """
    Add a comment to an incident.
    This view function handles both direct POST requests with a 'text' parameter
    and form submissions using CommentForm. The comment is associated with the
    incident identified by the primary key and the currently logged-in user.
    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the incident to which the comment will be added.
    Returns:
        HttpResponseRedirect: Redirects to the incident detail page after adding the comment.
    Raises:
        Http404: If no Incident matches the given primary key.
    """
    incident = get_object_or_404(Incident, pk=pk)
    
    if request.method == 'POST':
        if 'text' in request.POST:
            text = request.POST.get('text')
            comment = Comment(incident=incident, text=text, created_by=request.user)
            comment.save()
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.incident = incident
                comment.created_by = request.user
                comment.save()
    
    return redirect('incident_detail', pk=pk)


def process_incident_files(request: object, incident, files: list) -> int:
    """
    Process uploaded files and associate them with the incident.
    This function saves each uploaded file as an IncidentFile object linked to the given incident.
    It handles potential errors during the file save process and provides feedback through
    Django messages framework.
    Args:
        request: The HTTP request object, used for accessing the current user and adding messages.
        incident: The Incident object to associate the files with.
        files: A collection of file objects to process and save.
    Returns:
        int: The number of files successfully saved.
    Raises:
        Does not raise exceptions directly; exceptions during file save are caught and reported
        as error messages.
    """
    """Process uploaded files and associate them with the incident"""
    file_count = 0
    for file in files:
        try:
            incident_file = IncidentFile(
                incident=incident,
                file=file,
                filename=file.name,
                content_type=file.content_type,
                uploaded_by=request.user
            )
            incident_file.save()
            file_count += 1
            print(f"Saved file: {file.name}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            messages.error(request, f"Erreur lors de l'upload du fichier {file.name}: {str(e)}")
    
    if file_count > 0:
        messages.success(request, f"{file_count} fichier(s) uploadé(s) avec succès.")
    
    return file_count


def handle_transaction(request: object, action_func, success_message: str, error_prefix: str) -> any:
    """
    Execute a function within a transaction with proper error handling.
    
    This function provides a standardized way to execute database operations within
    a transaction context, handling success and error cases appropriately.
    
    Parameters
    ----------
    request : HttpRequest
        The request object to attach messages to
    action_func : callable
        Function to execute within the transaction
    success_message : str
        Message to display to the user upon successful completion
    error_prefix : str
        Text to prepend to error messages
        
    Returns
    -------
    Any
        Returns the result of action_func() if successful, None otherwise
        
    Notes
    -----
    - The transaction is managed automatically by Django
    - In case of exception, the error is printed to console with a traceback
      and an error message is shown to the user
    """
    """Execute a function within a transaction with proper error handling"""
    try:
        with transaction.atomic():
            result = action_func()
            messages.success(request, success_message)
            return result
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        messages.error(request, f"{error_prefix}: {str(e)}")
        return None


@login_required
def create_incident(request):
    """
    Create an incident record with associated links and files.
    This view handles both the GET request to display the incident creation form,
    and the POST request to process the submitted form data and create a new incident.
    The function performs the following operations:
    1. Validates the incident form and link formset
    2. Creates a new incident record associated with the current user
    3. Adds default values for required fields if not provided
    4. Processes any uploaded files and associates them with the incident
    5. Uses transactions to ensure database consistency
    Args:
        request: The HTTP request object containing form data and user information
    Returns:
        - On GET: Rendered form template for creating a new incident
        - On successful POST: Redirects to the detail view of the created incident
        - On validation error: Redisplays the form with error messages
    Raises:
        Various exceptions during file handling or database operations which are caught,
        logged and displayed to the user as error messages
    """
    if request.method == 'POST':
        # Remove request.FILES from the form - we'll handle files separately
        form = IncidentForm(request.POST)
        link_formset = LinkFormSet(request.POST, prefix='links')
        files = request.FILES.getlist('files')
        
        # More detailed debugging
        print("POST data received:", request.POST)
        print("FILES received:", request.FILES)
        print(f"Number of files: {len(files)}")
        
        if validate_forms(request, form, link_formset):
            def save_incident():
                # Enregistrer l'incident même s'il manque certaines valeurs
                incident = form.save(commit=False)
                incident.created_by = request.user
                
                # Assurer la présence de toutes les valeurs requises
                if not incident.start_date:
                    from django.utils import timezone
                    incident.start_date = timezone.now()
                
                if not incident.details:
                    incident.details = "Détails à ajouter"
                
                if not incident.resolution_process:
                    incident.resolution_process = "Processus de résolution à définir"
                
                if not incident.impact:
                    incident.impact = "Impact à évaluer"
                
                # Sauvegarder l'incident avec des traces de débogage
                print("Saving incident with data:", vars(incident))
                incident.save()
                print(f"Incident saved with ID: {incident.id}")
                
                # Important - Make sure to set the instance before saving formset
                link_formset.instance = incident
                link_formset.save()
                print("Link formset saved")
                
                # Traitement des fichiers
                process_incident_files(request, incident, files)
                
                return incident
            
            incident = handle_transaction(
                request,
                save_incident,
                'Incident créé avec succès.',
                'Une erreur s\'est produite lors de la création de l\'incident'
            )
            
            if incident:
                return redirect('incident_detail', pk=incident.id)
    else:
        form = IncidentForm()
        link_formset = LinkFormSet(prefix='links')
    
    return render(request, 'incidents/incidents_form.html', {
        'form': form,
        'link_formset': link_formset,
        'status_choices': Incident.STATUS_CHOICES,
        'severity_choices': Severity.choices
    })
    
    
@login_required
def update_incident(request, pk):
    """
    View function to update an existing incident.
    This function handles both GET and POST requests:
    - GET: Displays the form with existing incident data for editing
    - POST: Processes the submitted form data to update the incident
    The function fetches the incident by primary key, validates form data,
    processes any linked files, and handles the database transaction.
    Args:
        request (HttpRequest): The HTTP request object
        pk (int): Primary key of the incident to update
    Returns:
        HttpResponse: Renders the incident form template or redirects to 
                     the incident detail page after successful update
    Raises:
        Http404: If no incident with the given primary key exists
    """
    incident = get_object_or_404(Incident, pk=pk)
    
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        link_formset = LinkFormSet(request.POST, instance=incident, prefix='links')
        files = request.FILES.getlist('files')
        
        print("POST data received for update:", request.POST)
        print("FILES received for update:", request.FILES)
        
        if validate_forms(request, form, link_formset):
            def update_incident_data():
                form.save()
                print(f"Incident {incident.id} updated")
                
                link_formset.save()
                print("Link formset saved in update")
                
                # Process files
                process_incident_files(request, incident, files)
                
                return incident
            
            updated_incident = handle_transaction(
                request,
                update_incident_data,
                'Incident updated successfully.',
                'Une erreur s\'est produite lors de la mise à jour de l\'incident'
            )
            
            if updated_incident:
                return redirect('incident_detail', pk=incident.pk)
    else:
        form = IncidentForm(instance=incident)
        link_formset = LinkFormSet(instance=incident, prefix='links')
    
    return render(request, 'incidents/incidents_form.html', {
        'form': form,
        'link_formset': link_formset,
        'status_choices': Incident.STATUS_CHOICES,
        'severity_choices': Severity.choices
    })