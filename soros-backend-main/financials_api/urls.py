from django.urls import path

from financials_api.views.rag_view import RAGView
from financials_api.views.pairs_view import PairTradingView

urlpatterns = [
    path('ragbot/', RAGView.as_view(), name='ragbot'),
    path('pairs/', PairTradingView.as_view(), name='pair-trading'),
]
