from jinja2 import Environment, FileSystemLoader
import os


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

my_file = os.path.join(THIS_FOLDER, '/template/.')
print(my_file)
env = Environment(loader=FileSystemLoader(THIS_FOLDER))
template = env.get_template("report_template.html")

print(template)
