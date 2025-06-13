from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from models.KubernetesRole import KubernetesRole
import bcrypt
import os
import copy


class VMContext:
    def __init__(self, 
        users: list[dict[
            "username": str,
            "password": str,
            "sudo": bool
        ]],
        vm_name: str,
        k8s_dependencies: KubernetesRole = KubernetesRole.NONE,
        install_dependencies: str = None
    ):
        
        # Hash password
        self.users = copy.deepcopy(users)
        salt = bcrypt.gensalt()
        for user in self.users:
            user["password"] = bcrypt.hashpw(password=user["password"].encode('utf-8'), salt=salt).decode('utf-8')
        
        self.vm_name = vm_name
        self.k8s_dependencies = k8s_dependencies
        self.install_dependencies = install_dependencies


    def __build_context(self) -> dict:
        context = {}
        for name, val in vars(self).items():
            if name == "k8s_dependencies":
                if val:
                    with open(f"{os.getcwd()}/resources/scripts/k8s_dependencies.sh") as file:
                        context[name] = file.read()
                    
                    if val == KubernetesRole.CONTROL_PLANE:
                        with open(f"{os.getcwd()}/resources/scripts/init_control_plane.sh") as file:
                            context[name] += '\n' + file.read()
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
