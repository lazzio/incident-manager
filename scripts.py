import subprocess

def tests():
    """Execute tests"""
    return subprocess.call(["pytest"])

def lint():
    """Linter le code Django avec des outils spécifiques"""    
    print("Linting du code Django...")
    
    # Exécuter pylint avec configuration Django
    pylint_result = subprocess.run(["pylint", "--django", "--load-plugins=pylint_django", "votre_app_django"], check=False)
    
    # Exécuter flake8
    flake8_result = subprocess.run(["flake8", "votre_app_django"], check=False)
    
    # Exécuter isort pour vérifier l'ordre des imports
    isort_result = subprocess.run(["isort", "--check", "--diff", "votre_app_django"], check=False)
    
    # Exécuter django-lint si installé
    djlint_result = subprocess.run(["djlint", "votre_app_django/templates/", "--check"], check=False)
    
    # Vérifier les modèles Django avec check
    django_check = subprocess.run(["django-admin", "check", "--deploy"], check=False)
    
    # Retourner un code d'erreur si l'un des outils a échoué
    success = all(
        result.returncode == 0 
        for result in [pylint_result, flake8_result, isort_result, djlint_result, django_check]
    )
    
    if success:
        print("✅ Lint réussi!")
        return 0
    else:
        print("❌ Des problèmes de lint ont été détectés.")
        return 1

def dev():
    """Run development server"""
    return subprocess.call(["python", "manage.py", "runserver"])

def migrate():
    """Apply migrations"""
    subprocess.call(["python", "manage.py", "makemigrations"])
    subprocess.call(["python", "manage.py", "migrate"])
    return 0
