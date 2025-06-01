from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import os


class VMContext:
    def __init__(self, users: list[dict[
            "username": str,
            "password": str,
            "sudo": bool
        ]], k8s_dependencies: bool = False, install_dependencies: str = None):
        self.users = users
        self.k8s_dependencies = k8s_dependencies
        self.install_dependencies = install_dependencies


    def __build_context(self) -> dict:
        context = {}
        for name, val in vars(self).items():
            if name == "k8s_dependencies":
                if val:
                    with open(f"{os.getcwd()}/resources/scripts/k8s_dependencies.sh") as file:
                        context[name] = file.read()
            else:
                context[name] = val
        return context

    
    def gen_user_data(self, path: Path) -> Path:
        if not path.exists():
            raise Exception(f"Error: dir {path} doesn't exist.")

        context = self.__build_context()

        # Set the path to the directory containing user-data template
        template_path = Path(f"{os.getcwd()}/resources/templates/user-data.j2")

        # Prepare template environment
        env = Environment(
            loader=FileSystemLoader(template_path.parent),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template(template_path.name)
        
        # Render the template
        rendered_output = template.render(**context)

        # Write to user-data file
        output_path = f"{path}/user-data"
        with open(output_path, 'w') as f:
            f.write(rendered_output)

        print(f"'user-data' generated at {output_path}")
        return Path(output_path)
