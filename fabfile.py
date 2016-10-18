from fabric.api import *
from fabric.network import ssh

env.hosts = ['dsuriano@66.228.55.9:1021']
env.activate = 'source /webapps/cmwc_env/bin/activate'

def deploy():
  with prefix(env.activate):
    with cd('/webapps/cmwc_env/cmwc/'):
      run("pip install -r requirements.txt")
      run("git remote set-url origin git@github.com:dougsuriano/NACCC 2014git")
      run("git pull")
      run("python manage.py collectstatic --noinput")
      run("python manage.py migrate")
      run("sudo supervisorctl restart all")



def start():
    local("python manage.py runserver 0.0.0.0:8000")