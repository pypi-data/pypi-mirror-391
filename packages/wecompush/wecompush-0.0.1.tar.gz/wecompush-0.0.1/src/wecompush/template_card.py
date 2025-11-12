class TemplateCard:
    class Source:
        def __init__(self, icon_url: str = None, desc: str = None, desc_color=0):
            self.icon_url = icon_url
            self.desc = desc
            self.desc_color = desc_color

        def __str__(self):
            element = {'icon_url':self.icon_url,'desc':self.desc,'desc_color':self.desc_color,}
            valid_element = {k:v for k,v in element.items() if v}
            return 'source:'+str(valid_element)

    def __init__(self, card_type='text_notice'):
        self.card_type = card_type
        self.source = self.Source()

    def set_source(self, icon_url: str = None, desc: str = None, desc_color=0):
        self.source = {'icon_url': icon_url, 'desc': desc, 'desc_color': desc_color}


# a = TemplateCard()
# a.source.icon_url = 1
# print(a.source)
