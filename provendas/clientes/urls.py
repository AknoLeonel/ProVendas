# clientes/urls.py
from django.urls import path
from . import views # CORREÇÃO: Importa o módulo 'views' inteiro

urlpatterns = [
    # Suas rotas antigas
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/cadastrar-cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('cliente/editar-cliente/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('cliente/excluir/<int:cliente_id>/', views.excluir_cliente, name='excluir_cliente'),

    # Novas rotas do Fiado
    path('fiado/listar/<int:cliente_id>/', views.listar_fiados, name='listar_fiados'),
    path('fiado/adicionar/', views.adicionar_fiado, name='adicionar_fiado'),
    path('fiado/excluir/<int:fiado_id>/', views.excluir_fiado, name='excluir_fiado'),
    path('fiado/pagar/<int:cliente_id>/', views.pagar_fiado, name='pagar_fiado'),
]