from ninja import Router
from gpt_simplify.models import ClickedPaper
from .schemas import ClickedPaperOut

recommendation_api = Router()

@recommendation_api.get("/recommend")
def list_clicked_paper(request):
    # return ClickedPaper.objects.all()
    clicked_papers = ClickedPaper.objects.order_by('-clicked_count', '-published')[:10]
    # print(clicked_papers)
    return_list = []
    for clicked_paper in clicked_papers:
        cur_paper = {}
        cur_paper["Paper_ID"] = clicked_paper.paper_id
        cur_paper["Title_En"] = clicked_paper.title_en
        cur_paper["Title_Ja"] = clicked_paper.title_ja
        cur_paper["Authors"] = clicked_paper.author
        cur_paper["Categories"] = clicked_paper.categories
        cur_paper["Published"] = clicked_paper.published
        cur_paper["Content_En"] = clicked_paper.content_en
        cur_paper["Pdf_url"] = clicked_paper.pdf_url
        return_list.append(cur_paper)

    return return_list
    