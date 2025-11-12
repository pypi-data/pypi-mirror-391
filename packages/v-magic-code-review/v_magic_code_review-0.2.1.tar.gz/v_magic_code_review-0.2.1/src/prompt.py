import logging
import os
import textwrap
from collections import OrderedDict
from typing import List, Tuple

from util import ensure_folder


class Prompts:
    @classmethod
    def all_templates(cls) -> OrderedDict[str, str]:
        system_templates = cls._system_template()
        custom_templates = cls._custom_template()

        logging.debug("system templates: %s", system_templates)
        logging.debug("custom templates: %s", custom_templates)

        return OrderedDict(system_templates + custom_templates)

    @classmethod
    def list_template_names(cls) -> list[str]:
        return list(cls.all_templates().keys())

    @classmethod
    def create(
        cls,
        template_name: str,
        **kwargs
    ) -> str:
        prompt_structure = cls.all_templates()[template_name]
        prompt_structure = textwrap.dedent(prompt_structure).strip()
        return prompt_structure.format(**kwargs)

    @classmethod
    def _system_template(cls) -> List[Tuple[str, str]]:
        return cls._load_templates(os.path.join(os.path.dirname(__file__), 'prompts'))

    @classmethod
    def _custom_template(cls) -> List[Tuple[str, str]]:
        return cls._load_templates(os.path.expanduser('~/.local/share/v-cr/prompts'))

    @classmethod
    def _load_templates(cls, folder) -> List[Tuple[str, str]]:
        logging.debug("load_templates, folder: %s", folder)

        ensure_folder(folder)
        templates = []
        for filename in os.listdir(folder):
            template_name, ext = os.path.splitext(filename)
            if ext in ('.md', '.txt'):
                with open(os.path.join(folder, filename), 'r') as f:
                    templates.append((template_name, f.read()))
        return templates
