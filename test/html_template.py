from lxml import etree


class HTMLTemplate:
    def __init__(self, template_str):
        self.template = template_str

        # The default XMLParser does not accept tags with inline namespaces that
        # KaTeX produces such as <{https://some.uri}name />
        self.parser = etree.HTMLParser()
        self.element = etree.fromstring(template_str, parser=self.parser)
        self.element = self.strip_html(self.element)

    def __eq__(self, other):
        other_el = etree.fromstring(other, parser=self.parser)
        other_el = self.strip_html(other_el)
        return self.difference(self.element, other_el) is None

    def strip_html(self, element):
        # HTMLParser wraps everything in <html> and <body>. Get rid of that to
        # make the output clearer.
        return element.find("body")[0]

    def difference(self, template, element):
        if template.tag != element.tag:
            return ("", (template.tag, element.tag))

        for name, value in template.attrib.items():
            if element.attrib.get(name) != value:
                return (f"{template.tag}[{name}]", (value, element.attrib.get(name)))

        # Do not recurse into KaTeX output
        if (
            template.tag == "span"
            and "class" in template.attrib
            and template.attrib["class"] in ["katex", "katex-display"]
        ):
            return None

        if template.text != element.text:
            return (f"{template.tag}.text", (template.text, element.text))
        if template.tail != element.tail:
            return (f"{template.tag}.tail", (template.tail, element.tail))

        if len(template) != len(element):
            return (f"{template.tag}.children", (len(template), len(element)))

        for i, child_t, child_e in zip(range(len(template)), template, element):
            diff = self.difference(child_t, child_e)
            if diff is not None:
                return (f"{template.tag}[{i}].{diff[0]}", diff[1])

        return None

    def describe(self, other):
        """Describe the difference between this template and the HTML in other"""

        other_el = etree.fromstring(other, parser=self.parser)
        other_el = self.strip_html(other_el)
        diff = self.difference(self.element, other_el)

        if diff is None:
            return [""]

        return [
            "String does not match the template",
            f"There is a difference in element {diff[0]}",
            "",
            f"    {diff[1][0]!r} != {diff[1][1]!r}",
            "",
            "Template is:",
            "",
            self.template,
            "String is:",
            "",
            other,
        ]
