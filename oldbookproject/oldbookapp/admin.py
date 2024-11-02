from django.contrib import admin
from oldbookapp.models import Books, About,Contact,CustomUser

class BooksAdmin(admin.ModelAdmin):
    list_display = ('Book_Title', 'Book_Author', 'Year_Of_Publication', 'price')
    search_fields = ('Book_Title', 'Book_Author')
    list_filter = ('category',)  # Assuming 'category' is a field in your Books model

admin.site.register(Books, BooksAdmin)
admin.site.register(About)
admin.site.register(Contact)
admin.site.register(CustomUser)
