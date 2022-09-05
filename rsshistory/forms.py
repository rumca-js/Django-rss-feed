from django import forms
from .models import RssLinkDataModel, RssLinkEntryDataModel

# https://docs.djangoproject.com/en/4.1/ref/forms/widgets/

#class NewLinkForm(forms.Form):
#    """
#    New link form
#    """
#    class Meta:
#        model = LinkDataModel
#        fields = ['url', 'category', 'subcategory', 'artist', 'album', 'title', 'date_created']


class NewLinkForm(forms.Form):
    """
    New link form
    """
    url = forms.CharField(label='Url', max_length = 500)
    category = forms.CharField(label='Category', max_length = 100)
    subcategory = forms.CharField(label='Subcategory', max_length = 100)
    title = forms.CharField(label='Title', max_length = 200)

    class Meta:
        model = RssLinkDataModel

    def __init__(self, *args, **kwargs):
        init_obj = kwargs.pop('init_obj', ())

        super().__init__(*args, **kwargs)

        if init_obj != ():
            self.fields['url'] = forms.CharField(label='Url', max_length = 500, initial=init_obj.url)
            self.fields['category'] = forms.CharField(label='Category', max_length = 100, initial=init_obj.category)
            self.fields['subcategory'] = forms.CharField(label='Subcategory', max_length = 100, initial=init_obj.subcategory)
            self.fields['title'] = forms.CharField(label='Title', max_length = 100, initial=init_obj.title)
        else:
            from django.utils.timezone import now

    def to_model(self):
        url = self.cleaned_data['url']
        category = self.cleaned_data['category']
        subcategory = self.cleaned_data['subcategory']
        title = self.cleaned_data['title']

        record = RssLinkDataModel(url=url,
                                    title=title,
                                    category=category,
                                    subcategory=subcategory)

        return record


class ImportLinksForm(forms.Form):
    """
    Import links form
    """
    rawlinks = forms.CharField(widget=forms.Textarea(attrs={'name':'rawlinks', 'rows':30, 'cols':100}))


class SourcesChoiceForm(forms.Form):
    """
    Category choice form
    """

    category = forms.CharField(widget=forms.Select(choices=()))
    subcategory = forms.CharField(widget=forms.Select(choices=()))
    title = forms.CharField(widget=forms.Select(choices=()))

    def __init__(self, *args, **kwargs):
        self.args = kwargs.pop('args', ())
        super().__init__(*args, **kwargs)

    def get_filtered_objects(self):
        parameter_map = self.get_filter_args()
        self.filtered_objects = RssLinkDataModel.objects.filter(**parameter_map)
        return self.filtered_objects

    def create(self):
        # how to unpack dynamic forms
        # https://stackoverflow.com/questions/60393884/how-to-pass-choices-dynamically-into-a-django-form
        categories = self.get_filtered_objects_values('category')
        subcategories = self.get_filtered_objects_values('subcategory')
        title = self.get_filtered_objects_values('title')

        # custom javascript code
        # https://stackoverflow.com/questions/10099710/how-to-manually-create-a-select-field-from-a-modelform-in-django
        attr = {"onchange" : "this.form.submit()"}

        # default form value
        # https://stackoverflow.com/questions/604266/django-set-default-form-values
        category_init = self.get_init('category')
        subcategory_init = self.get_init('subcategory')
        title_init = self.get_init('title')

        self.fields['category'] = forms.CharField(widget=forms.Select(choices=categories, attrs=attr), initial=category_init)
        self.fields['subcategory'] = forms.CharField(widget=forms.Select(choices=subcategories, attrs=attr), initial=subcategory_init)
        self.fields['title'] = forms.CharField(widget=forms.Select(choices=title, attrs=attr), initial=title_init)

    def get_init(self, column):
        filters = self.get_filter_args()
        if column in filters:
            return filters[column]
        else:
            return "Any"

    def get_filtered_objects_values(self, field):
        values = set()
        values.add("Any")

        for val in self.filtered_objects.values(field):
            if str(val).strip() != "":
                values.add(val[field])

        dict_values = self.to_dict(values)

        return dict_values

    def to_dict(self, alist):
        result = []
        for item in sorted(alist):
            if item.strip() != "":
                result.append((item, item))
        return result

    def get_filter_args(self):
        parameter_map = {}

        category = self.args.get("category")
        if category and category != "Any":
           parameter_map['category'] = category

        subcategory = self.args.get("subcategory")
        if subcategory and subcategory != "Any":
           parameter_map['subcategory'] = subcategory

        title = self.args.get("title")
        if title and title != "Any":
           parameter_map['title'] = title

        return parameter_map


class EntryChoiceForm(forms.Form):
    """
    Category choice form
    """

    category = forms.CharField(widget=forms.Select(choices=()))
    subcategory = forms.CharField(widget=forms.Select(choices=()))
    title = forms.CharField(widget=forms.Select(choices=()))
    favourite = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        self.args = kwargs.pop('args', ())
        super().__init__(*args, **kwargs)

    def get_filtered_objects(self):
        source_parameter_map = self.get_source_filter_args()
        entry_parameter_map = self.get_entry_filter_args()

        self.entries = []
        self.sources = RssLinkDataModel.objects.filter(**source_parameter_map)

        if self.sources.exists():
            index = 0
            for obj in self.sources:
                entry_parameter_map["url"] = obj.url
                if index == 0:
                    self.entries = RssLinkEntryDataModel.objects.filter(**entry_parameter_map)
                else:
                    self.entries = self.entries | RssLinkEntryDataModel.objects.filter(**entry_parameter_map)
                index += 1
        else:
            self.entries = RssLinkEntryDataModel.objects.filter(**entry_parameter_map)

        return self.entries

    def create(self):
        # how to unpack dynamic forms
        # https://stackoverflow.com/questions/60393884/how-to-pass-choices-dynamically-into-a-django-form
        categories = self.get_filtered_objects_values('category')
        subcategories = self.get_filtered_objects_values('subcategory')
        title = self.get_filtered_objects_values('title')

        # custom javascript code
        # https://stackoverflow.com/questions/10099710/how-to-manually-create-a-select-field-from-a-modelform-in-django
        attr = {"onchange" : "this.form.submit()"}

        # default form value
        # https://stackoverflow.com/questions/604266/django-set-default-form-values
        category_init = self.get_source_init('category')
        subcategory_init = self.get_source_init('subcategory')
        title_init = self.get_source_init('title')

        self.fields['category'] = forms.CharField(widget=forms.Select(choices=categories, attrs=attr), initial=category_init)
        self.fields['subcategory'] = forms.CharField(widget=forms.Select(choices=subcategories, attrs=attr), initial=subcategory_init)
        self.fields['title'] = forms.CharField(widget=forms.Select(choices=title, attrs=attr), initial=title_init)
        self.fields['favourite'] = forms.BooleanField(required=False, initial=self.args.get('favourite'))

    def get_filtered_objects_values(self, field):
        values = set()
        values.add("Any")

        for val in self.sources.values(field):
            if str(val).strip() != "":
                values.add(val[field])

        dict_values = self.to_dict(values)

        return dict_values

    def get_source_init(self, column):
        filters = self.get_source_filter_args()
        if column in filters:
            return filters[column]
        else:
            return "Any"

    def to_dict(self, alist):
        result = []
        for item in sorted(alist):
            if item.strip() != "":
                result.append((item, item))
        return result

    def get_source_filter_args(self):
        parameter_map = {}

        category = self.args.get("category")
        if category and category != "Any":
           parameter_map['category'] = category

        subcategory = self.args.get("subcategory")
        if subcategory and subcategory != "Any":
           parameter_map['subcategory'] = subcategory

        title = self.args.get("title")
        if title and title != "Any":
           parameter_map['title'] = title

        return parameter_map

    def get_entry_filter_args(self):
        parameter_map = {}

        favourite = self.args.get("favourite")
        if favourite:
           parameter_map['favourite'] = True

        return parameter_map
