from .models import Papers, Keywords, Reads, Profile
import json


# Search Translated Title   for views.py
def search_titles(request_Paper_ID):
    if Papers.objects.filter(Paper_ID = request_Paper_ID).exists():
        content = Papers.objects.get(Paper_ID = request_Paper_ID)
        record = {
            "Paper_ID"   : content["Paper_ID"],
            "Title_En"   : content["Title_En"],
            "Title_Ja"   : content["Title_Ja"],
            "Authors"    : content["Authors"].split(","),
            "Categories" : content["Categories"].split(","),
            "Published"  : content["Published"],
            "Content_En" : content["Content_En"]
        }
        return record
    else:
        return {}

# Search Translated Content and Keywords    for views.py
def search_papers(request_Paper_ID):
    if not Papers.objects.filter(Paper_ID = request_Paper_ID).first()["Content_Ja"] is None:
        content = Papers.objects.get(Paper_ID = request_Paper_ID)
        # Add 1 to Search_num
        content["Search_num"] += 1
        content.save()
        # search keywords
        record = Keywords.objects.get(Paper_ID = request_Paper_ID)
        keywords = record["Keyword"].split(",")
        descriptions = record["Description"].split(",")

        output = {
            "Paper_ID"      : content["Paper_ID"],
            "Title_En"      : content["Title_En"],
            "Title_Ja"      : content["Title_Ja"],
            "Authors"       : content["Authors"].split(","),
            "Categories"    : content["Categories"].split(","),
            "Published"     : content["Published"],
            "Content_En"    : content["Content_En"],
            "Content_Ja"    : content["Content_Ja"],
            "Content_plain" : content["Content_plain"],
            "Pdf_url"       : content["Pdf_url"],
            "Keywords" : [{
                "Keyword"     : keywords[i],
                "Description" : descriptions[i]
                }
                for i in range(len(keywords))]
        }

        return output
    else:
        return {}



# Add translated title   for views.py
def add_title(title_data):  
    categories = ','.join(title_data["Categories"])
    authors    = ','.join(title_data["Authors"])
    paper_record = Papers(
        Paper_ID = title_data["Paper_ID"],
        Title_En = title_data["Title_En"],
        Title_Ja = title_data["Title_Ja"],
        Categories = categories,
        Authors = authors,
        Pdf_url = title_data["Pdf_url"],
        Published = title_data["Published"],
        Content_En = title_data["Content_En"],
        Content_Ja = None,
        Content_plain = None,
        Search_num = 0
    )
    paper_record.save()

# Add translated content
def add_content(paper_data):
    paper_record = Papers.objects.get(Paper_ID = paper_data["Paper_ID"])
    paper_record["Content_Ja"] = paper_data["Content_Ja"]
    paper_record["Content_plain"] = paper_data["Content_plain"]
    paper_record["Search_num"] = 1
    paper_record.save()

# Add keywords
def add_keywords(keyword_data):
    k_ds = ','.join(keyword_data["Keywords"])
    keywords     = []
    descriptions = []
    for i in k_ds:
        keywords.append(i["Keyword"])
        descriptions.append(i["Description"])
    keywords       = ','.join(keywords)
    descriptions   = ','.join(descriptions)
    keyword_record = Keywords(
        Paper_ID    = keyword_data["Paper_ID"],
        Keyword     = keywords,
        Description = descriptions,
    )
    keyword_record.save()


# add_content + add_keywords    for views.py
def add_content_keywords(paper_data, keyword_data):
    add_content(paper_data)
    add_keywords(keyword_data)



# After User login 

# Register
def add_user(user_data):
    user_record = Profile(
        User_ID = user_data["User_ID"],
        Name = user_data["Name"],
        Pass = user_data["Pass"]
    )
    user_record.save()


# Search User's history
def get_histry(request_User_ID):
    if Reads.objects.filter(Reader_ID = request_User_ID).exists():
        contents = Reads.objects.filter(Reader_ID = request_User_ID)
        records = {
            "Histries" : [{
                "Paper_ID" : content["Paper_ID"],
                "Title_En" : content["Title_En"],
                "Title_Ja" : content["Title_Ja"]
        }
        for content in contents
        ]}
        return records
    else:
        return {}


# def add_histry(read_data):




# delete all data in the database (for supervisor)

def delete():
    Papers.objects.all().delete()
    Keywords.objects.all().delete()
    Profile.objects.all().delete()
    Reads.objects.all().delete()
