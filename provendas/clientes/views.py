# clientes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
import json
import time
import random
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Cliente, Fiado
from estoque.models import Produto
from caixa.models import Caixa, CaixaPdv, ProdutoCaixaPdv
from configuracoes.models import Configuracao
from decimal import Decimal


from .models import Cliente
from .forms import ClienteForm

def listar_clientes(request):
    clientes = Cliente.objects.all()  # Busca todos os clientes cadastrados
    form = ClienteForm()

    # Formatar a data de nascimento de cada cliente para o formato ISO 'YYYY-MM-DD'
    for cliente in clientes:
        if cliente.data_nascimento:
            cliente.data_nascimento = cliente.data_nascimento.strftime('%Y-%m-%d')  # Formato ISO

    return render(request, 'clientes/listar_clientes.html', {'clientes': clientes, 'form': form})

def editar_cliente(request, cliente_id):
    # Obtém o cliente com o ID fornecido na URL
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            # Atualiza o cliente sem tratar campos de limite de crédito
            form.save()
            messages.success(request, 'Cliente editado com sucesso!')
            return redirect('listar_clientes')
        else:
            print(form.errors)  # Ajuda a depurar caso o formulário tenha erros
    
    return redirect('listar_clientes')


def cadastrar_cliente(request):
    if request.method == 'POST':
        # Captura os dados diretamente do request.POST
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        cpf = request.POST.get('cpf')
        telefone = request.POST.get('telefone')
        data_nascimento = request.POST.get('data_nascimento')
        endereco = request.POST.get('endereco')
        cidade = request.POST.get('cidade')
        estado = request.POST.get('estado')
        cep = request.POST.get('cep')
        status = request.POST.get('status')
        
        # Criação de um novo cliente sem campos de limite de crédito
        cliente = Cliente(
            nome=nome,
            email=email,
            cpf=cpf,
            telefone=telefone,
            data_nascimento=data_nascimento,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            cep=cep,
            status=status
        )
        cliente.save()

        # Mensagem de sucesso
        messages.success(request, f'Cliente "{nome}" cadastrado com sucesso!')
        return redirect('listar_clientes')  # Redireciona para a lista de clientes

    return redirect('listar_clientes')


def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, f'O cliente {cliente.nome} foi excluído com sucesso.')
        return redirect(reverse('listar_clientes'))  # Substitua 'listar_clientes' pelo nome da view de listagem de clientes.
    return redirect(reverse('listar_clientes'))

def listar_fiados(request, cliente_id):
    """Retorna os fiados em aberto de um cliente via AJAX"""
    if request.method == 'GET':
        cliente = get_object_or_404(Cliente, id=cliente_id)
        # Busca apenas os fiados que AINDA NÃO FORAM PAGOS
        fiados_pendentes = Fiado.objects.filter(cliente=cliente, pago=False).order_by('data_registro')
        
        dados = []
        for f in fiados_pendentes:
            # Formata a data para ficar bonitinha
            data_formatada = timezone.localtime(f.data_registro).strftime('%d/%m/%Y %H:%M')
            dados.append({
                'id': f.id,
                'data': data_formatada,
                'produto': f.produto.nome,
                'quantidade': f.quantidade,
                'valor_total': str(f.valor_total)
            })
            
        return JsonResponse({'success': True, 'fiados': dados})

def adicionar_fiado(request):
    """Adiciona um novo produto na conta do cliente (Baixa estoque)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente_id = data.get('cliente_id')
            produto_id = data.get('produto_id')
            quantidade = int(data.get('quantidade', 1))

            cliente = get_object_or_404(Cliente, id=cliente_id)
            produto = get_object_or_404(Produto, id=produto_id)

            if quantidade <= 0:
                return JsonResponse({'success': False, 'message': 'Quantidade inválida.'})

            # Calcula o total
            valor_total = Decimal(str(quantidade)) * produto.preco_de_venda

            # Baixa no estoque
            if produto.controle_estoque:
                produto.quantidade_estoque -= quantidade
                produto.save()

            # Cria o registro da dívida
            Fiado.objects.create(
                cliente=cliente,
                produto=produto,
                quantidade=quantidade,
                valor_total=valor_total
            )

            return JsonResponse({'success': True, 'message': 'Lançado com sucesso!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

def excluir_fiado(request, fiado_id):
    """Cancela um lançamento feito errado e devolve pro estoque"""
    if request.method == 'POST':
        try:
            fiado = get_object_or_404(Fiado, id=fiado_id)
            produto = fiado.produto

            # Devolve o estoque se for gerenciável
            if produto.controle_estoque:
                produto.quantidade_estoque += fiado.quantidade
                produto.save()

            fiado.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

def pagar_fiado(request, cliente_id):
    """Liquida a dívida do cliente e joga o valor como venda no Caixa"""
    if request.method == 'POST':
        try:
            cliente = get_object_or_404(Cliente, id=cliente_id)
            fiados_pendentes = Fiado.objects.filter(cliente=cliente, pago=False)

            if not fiados_pendentes.exists():
                return JsonResponse({'success': False, 'message': 'O cliente não tem dívidas pendentes.'})

            # Verifica Caixa Aberto (Igual no PDV)
            configuracao = Configuracao.objects.first()
            gerenciar_caixa = configuracao.gerenciar_abertura_fechamento_caixa if configuracao else False
            caixa = None
            
            if gerenciar_caixa:
                caixa = Caixa.objects.filter(status='Aberto', usuario=request.user).first()
                if not caixa:
                    return JsonResponse({'success': False, 'message': 'Você precisa abrir o caixa primeiro.'})

            total_pago = sum(f.valor_total for f in fiados_pendentes)

            # Gera um numero de pedido unico (Igual da comanda)
            timestamp = str(int(time.time()))[-4:]
            numero_aleatorio = random.randint(1000, 9999)
            num_pedido = f"FIADO-{timestamp}{numero_aleatorio}"

            # 1. Cria uma Venda Direta no Caixa para registrar a entrada de dinheiro
            caixa_pdv = CaixaPdv.objects.create(
                caixa=caixa,
                numero_pedido=num_pedido,
                vendedor=request.user,
                cliente=cliente,
                desconto=0,
                total=total_pago,
                status="Finalizado",
                payment_method="Dinheiro" # Fiado normalmente se paga em dinheiro (Você pode evoluir depois para pedir a forma)
            )

            # 2. Transfere os produtos do Fiado para o Cupom da Venda (Sem baixar estoque de novo)
            for f in fiados_pendentes:
                ProdutoCaixaPdv.objects.create(
                    caixa_pdv=caixa_pdv,
                    produto=f.produto,
                    quantidade=f.quantidade,
                    preco_unitario=f.produto.preco_de_venda,
                    total=f.valor_total
                )
                # 3. Marca o fiado como pago
                f.pago = True
                f.data_pagamento = timezone.now()
                f.save()

            return JsonResponse({'success': True, 'message': 'Dívida paga com sucesso!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})