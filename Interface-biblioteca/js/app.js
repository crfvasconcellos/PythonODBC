/* ==========================================================================
   Sistema da Biblioteca · comportamento da interface
   (CRUD e ações avançadas preparados para API; sem ligação direta com o banco)
   ========================================================================== */
(() => {
  'use strict';

  /* ------------------------------------------------------------------------
     1. FUNDO EM CARROSSEL
     Para incluir mais fotos, coloque o arquivo em imgs/fundos/ e acrescente
     o caminho na lista abaixo.
     ------------------------------------------------------------------------ */
  const FUNDOS = [
    'imgs/fundos/fundo-01.jpg',
    'imgs/fundos/fundo-02.jpg',
    'imgs/fundos/fundo-03.jpg',
    'imgs/fundos/fundo-04.jpg',
    'imgs/fundos/fundo-05.jpg',
    'imgs/fundos/fundo-06.jpg',
    'imgs/fundos/fundo-07.jpg',
    'imgs/fundos/fundo-08.jpg',
    'imgs/fundos/fundo-09.jpg',
    'imgs/fundos/fundo-10.jpg',
    'imgs/fundos/fundo-11.jpg',
    'imgs/fundos/fundo-12.jpg',
    'imgs/fundos/fundo-13.jpg',
    'imgs/fundos/fundo-14.jpg',
    'imgs/fundos/fundo-15.jpg',
    'imgs/fundos/fundo-16.jpg',
    'imgs/fundos/fundo-17.jpg',
    'imgs/fundos/fundo-18.jpg',
  ];
  const INTERVALO_MS = 9000; // tempo que cada foto fica na tela
  const FADE_MS = 1800;      // duração da transição entre fotos (igual ao transition do CSS)

  function embaralhar(lista) {
    const copia = [...lista];
    for (let i = copia.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copia[i], copia[j]] = [copia[j], copia[i]];
    }
    return copia;
  }

  function carregarImagem(url) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => resolve(true);
      img.onerror = () => resolve(false);
      img.src = url;
    });
  }

  function iniciarCarrossel() {
    const camadas = Array.from(document.querySelectorAll('.fundo__camada'));
    if (camadas.length < 2 || FUNDOS.length === 0) return;

    const ordem = embaralhar(FUNDOS); // a ordem muda a cada vez que a página abre
    let indice = -1;
    let ativa = 1;                    // camada que está na tela (a primeira troca usa a 0)
    let ocupado = false;
    let apagar = null;

    function mostrar(url) {
      const entrando = camadas[1 - ativa];
      const saindo = camadas[ativa];

      entrando.style.backgroundImage = `url("${url}")`;
      // a foto nova aparece POR CIMA da atual, sem "piscada" escura no meio do fade
      entrando.style.zIndex = '2';
      saindo.style.zIndex = '1';
      // reinicia o zoom lento da camada que vai entrar
      entrando.classList.remove('fundo__camada--zoom');
      void entrando.offsetWidth;
      entrando.classList.add('fundo__camada--zoom', 'fundo__camada--visivel');

      // a foto anterior só é apagada depois que a nova cobriu a tela
      clearTimeout(apagar);
      apagar = setTimeout(() => saindo.classList.remove('fundo__camada--visivel'), FADE_MS + 100);
      ativa = 1 - ativa;
    }

    async function proxima() {
      if (ocupado) return;
      ocupado = true;
      // pula fotos que não carregarem (arquivo faltando, por exemplo)
      for (let tentativas = 0; tentativas < ordem.length; tentativas++) {
        indice = (indice + 1) % ordem.length;
        if (await carregarImagem(ordem[indice])) {
          mostrar(ordem[indice]);
          carregarImagem(ordem[(indice + 1) % ordem.length]); // já deixa a próxima no cache
          break;
        }
      }
      ocupado = false;
    }

    proxima();
    setInterval(() => { if (!document.hidden) proxima(); }, INTERVALO_MS);
  }

  /* ------------------------------------------------------------------------
     2. TELAS
     ------------------------------------------------------------------------ */
  const telas = {
    principal: document.getElementById('tela-principal'),
    avancada:  document.getElementById('tela-avancada'),
    saida:     document.getElementById('tela-saida'),
    listagem:  document.getElementById('tela-listagem'),
    cadastro:  document.getElementById('tela-cadastro'),
    atualizacao: document.getElementById('tela-atualizacao'),
    exclusao:  document.getElementById('tela-exclusao'),
    autor:     document.getElementById('tela-autor'),
    joins:     document.getElementById('tela-joins'),
    resultadoJoin: document.getElementById('tela-join-resultado'),
    relatorioGenero: document.getElementById('tela-relatorio-genero'),
    buscaCatalogo: document.getElementById('tela-busca-catalogo'),
    estantesVazias: document.getElementById('tela-estantes-vazias'),
    acervoCritico: document.getElementById('tela-acervo-critico'),
    autoresUnicos: document.getElementById('tela-autores-unicos'),
    faixaExemplares: document.getElementById('tela-faixa-exemplares'),
    autoresMultigenero: document.getElementById('tela-autores-multigenero'),
    estantes: document.getElementById('tela-estantes'),
  };

  let atualizarSliders = () => {};

  function mostrarTela(nome) {
    for (const [chave, elemento] of Object.entries(telas)) {
      if (elemento) elemento.hidden = chave !== nome;
    }
    if (nome === 'avancada') document.getElementById('lista-avancada').scrollTop = 0;
    if (nome === 'listagem') document.getElementById('lista-livros').scrollTop = 0;
    if (nome === 'autor') document.getElementById('lista-autor').scrollTop = 0;
    if (nome === 'resultadoJoin') document.getElementById('lista-join').scrollTop = 0;
    if (nome === 'relatorioGenero') document.getElementById('lista-relatorio-genero').scrollTop = 0;
    if (nome === 'buscaCatalogo') document.getElementById('lista-busca-catalogo').scrollTop = 0;
    if (nome === 'estantesVazias') document.getElementById('lista-estantes-vazias').scrollTop = 0;
    if (nome === 'acervoCritico') document.getElementById('lista-acervo-critico').scrollTop = 0;
    if (nome === 'autoresUnicos') document.getElementById('lista-autores-unicos').scrollTop = 0;
    if (nome === 'faixaExemplares') document.getElementById('lista-faixa-exemplares').scrollTop = 0;
    if (nome === 'autoresMultigenero') document.getElementById('lista-autores-multigenero').scrollTop = 0;
    if (nome === 'estantes') document.getElementById('lista-gerenciar-estantes').scrollTop = 0;
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
    // leva o foco para o título da nova tela (leitores de tela anunciam a mudança)
    telas[nome].querySelector('h1').focus({ preventScroll: true });
  }

  function sairDoSistema() {
    // Os navegadores só deixam um script fechar abas abertas por script (window.open).
    // Numa aba aberta pelo usuário o comando é ignorado, então mostramos a despedida.
    window.close();
    mostrarTela('saida');
  }

  /* ------------------------------------------------------------------------
     3. CRUD LOCAL E PREPARAÇÃO PARA A API
     A aplicação Python disponibilizada usa pyodbc e terminal, não expõe HTTP.
     Por isso a URL fica vazia: nada é enviado ao banco nesta etapa.

     QUANDO A API HTTP ESTIVER PRONTA, configurar API_BASE_URL e adaptar, caso
     necessário, as rotas abaixo ao contrato do servidor:
       GET    /livros                 -> array de livros (ou {livros: [...]})
       POST   /livros                 -> JSON de um novo livro
       PUT    /livros/{id_livro}      -> JSON com os novos dados
       DELETE /livros/{id_livro}      -> sucesso: HTTP 200 ou 204
       GET    /livros/por-autor?autor=... -> {total: N, livros: [...]} ou {total: N}
           A FUNCTION existente conta livros; uma lista detalhada é OPCIONAL.
       POST   /livros/procedure       -> mesmos campos do cadastro, mas via PROCEDURE
       GET    /consultas/joins/{codigo} -> array de linhas ou {registros: [...]}
           codigo = natural | inner | left | right | full
           A API deverá executar o SQL correspondente, não SQL vindo do navegador.
       GET    /relatorios/estatisticas-por-genero?media_minima=5
           -> {registros: [{genero, media_exemplares, minimo_exemplares, maximo_exemplares}]}
              ou array direto; HAVING AVG(numero_de_exemplares) > media_minima.
       GET    /catalogo/busca?termo=palavra
           -> {registros: [{titulo_destaque, catalogo_completo, genero_curto,
                            tamanho_titulo}]} ou array direto; ILIKE no nome/autor.
           Ordem preservada da consulta SQL (autor ASC, exemplares DESC).
       GET    /auditoria/estantes-vazias
           -> {registros: [{id_estante, dominio_lado_1}]} ou array direto
              EXCEPT: retorna somente estantes SEM livro associado.
       GET    /analises/acervo-critico?genero_alvo=...&genero_comparacao=...
           -> {registros: [{nome, numero_de_exemplares}]} ou array direto.
              genero_alvo filtra estantes.dominio_lado_1, NÃO livros.genero.
              SOME: exemplares > ao menos UM valor dos livros de gênero comparado.
       GET    /autores/unicos
           -> {registros: [{autor}]} ou array de strings / objetos.
              DISTINCT autor, sem nulos, ordenação ASC.
       GET    /livros/por-faixa?minimo=2&maximo=10
           -> {registros: [{nome, autor, numero_de_exemplares}]} ou array direto.
              BETWEEN é inclusivo e a ordenação é por exemplares DESC.
       GET    /relatorios/autores-multigenero?genero1=Fantasia&genero2=Terror
           -> {registros: [{autor}]} ou array de strings / objetos.
              INTERSECT retorna uma vez os autores presentes nos DOIS gêneros.
              O SQL não especifica ordenação para esta consulta.

     Operações (inclusive consultas) são mantidas em localStorage até confirmação
     HTTP de sucesso. Os endpoints acima são um contrato SUGERIDO para a futura API.
     Isso não equivale a gravar no PostgreSQL e não é uma API funcional.
     ------------------------------------------------------------------------ */
  // API servida por api.py (mesma origem). Se abrir o HTML direto do disco, usa localhost:8000.
  const API_BASE_URL = location.protocol === 'file:' ? 'http://127.0.0.1:8000/api' : '/api';
  const CHAVE_PENDENCIAS = 'biblioteca_operacoes_pendentes_v1';
  const listaLivros = document.getElementById('lista-livros');
  const modeloLivro = document.getElementById('modelo-livro');
  const modeloVazio = document.getElementById('catalogo-vazio').cloneNode(true);

  function lerPendencias() {
    try {
      const dados = JSON.parse(localStorage.getItem(CHAVE_PENDENCIAS) || '[]');
      return Array.isArray(dados) ? dados : [];
    } catch (erro) {
      return [];
    }
  }

  function gravarPendencias(pendencias) {
    try {
      localStorage.setItem(CHAVE_PENDENCIAS, JSON.stringify(pendencias));
      return true;
    } catch (erro) {
      return false;
    }
  }

  function atualizarAvisoPendencias() {
    const quantidade = lerPendencias().length;
    const aviso = document.getElementById('catalogo-pendencias');
    aviso.hidden = quantidade === 0;
    aviso.textContent = quantidade === 1
      ? '1 operação salva neste navegador, aguardando envio à API.'
      : `${quantidade} operações salvas neste navegador, aguardando envio à API.`;
    document.getElementById('botao-sincronizar').hidden = !API_BASE_URL || quantidade === 0;
  }

  function criarPendencia(tipo, dados) {
    const pendencias = lerPendencias();
    const nova = {
      chave: `${Date.now()}-${Math.random().toString(36).slice(2, 12)}`,
      tipo,
      dados,
      criado_em: new Date().toISOString()
    };
    // Não descartar operações antigas silenciosamente.
    if (pendencias.length >= 500 || !gravarPendencias([...pendencias, nova])) return null;
    atualizarAvisoPendencias();
    return nova;
  }

  function retirarPendencia(chave) {
    gravarPendencias(lerPendencias().filter((op) => op.chave !== chave));
    atualizarAvisoPendencias();
  }

  function mensagemFormulario(tipo, texto, estado = 'aviso') {
    const identificador = tipo === 'cadastro_procedure' ? 'cadastro' : tipo;
    const campo = document.getElementById(`mensagem-${identificador}`);
    campo.textContent = texto;
    campo.dataset.tipo = estado;
  }

  function extrairLivros(resposta) {
    if (Array.isArray(resposta)) return resposta;
    if (resposta && Array.isArray(resposta.livros)) return resposta.livros;
    if (resposta && Array.isArray(resposta.data)) return resposta.data;
    throw new Error('A resposta da API não contém uma lista de livros.');
  }

  function criarFichaLivro(livro) {
    const ficha = modeloLivro.content.firstElementChild.cloneNode(true);
    const valores = {
      nome: livro.nome ?? 'Não informado',
      genero: livro.genero ?? 'Não informado',
      numero_de_exemplares: livro.numero_de_exemplares ?? 'Não informado',
      autor: livro.autor ?? 'Não informado',
      pode_ser_emprestado: livro.pode_ser_emprestado === true || livro.pode_ser_emprestado === 1
        ? 'Sim' : livro.pode_ser_emprestado === false || livro.pode_ser_emprestado === 0
          ? 'Não' : 'Não informado'
    };
    for (const [campo, valor] of Object.entries(valores)) {
      ficha.querySelector(`[data-campo="${campo}"]`).textContent = String(valor);
    }
    const id = livro.id_livro ?? livro.id;
    ficha.querySelector('[data-campo="id_livro"]').textContent = id == null ? '' : `ID: ${id}`;
    return ficha;
  }

  function preencherFichasLivro(container, livros) {
    const fragmento = document.createDocumentFragment();
    livros.forEach((livro) => fragmento.append(criarFichaLivro(livro)));
    container.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  function mostrarEstado(container, titulo, descricao) {
    const estado = document.createElement('div');
    estado.className = 'estado-vazio';
    const cabecalho = document.createElement('h2');
    cabecalho.textContent = titulo;
    const texto = document.createElement('p');
    texto.textContent = descricao;
    estado.append(cabecalho, texto);
    container.replaceChildren(estado);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  function renderizarLivros(livros, erro = false) {
    listaLivros.replaceChildren();
    if (!livros.length) {
      const vazio = modeloVazio.cloneNode(true);
      vazio.querySelector('h2').textContent = erro
        ? 'Não foi possível consultar os livros.'
        : 'Nenhum livro registrado ainda.';
      vazio.querySelector('p').textContent = erro
        ? 'A API não respondeu. Tente novamente após verificar a conexão.'
        : API_BASE_URL
          ? 'O banco de dados não retornou nenhum livro cadastrado.'
          : 'A listagem ficará disponível quando a API estiver conectada ao banco de dados.';
      listaLivros.append(vazio);
    } else {
      preencherFichasLivro(listaLivros, livros);
    }
    const resumo = document.getElementById('catalogo-resumo');
    resumo.textContent = erro ? 'Falha na comunicação com a API.'
      : !API_BASE_URL ? 'Acervo: aguardando integração com a API.'
      : livros.length === 1 ? '1 livro registrado no banco de dados.'
      : `${livros.length} livros registrados no banco de dados.`;
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  async function obterLivrosDaAPI() {
    const resposta = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/livros`, {
      headers: { Accept: 'application/json' }
    });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    return extrairLivros(await resposta.json());
  }

  async function abrirListagem() {
    mostrarTela('listagem');
    atualizarAvisoPendencias();
    if (!API_BASE_URL) {
      renderizarLivros([]);
      return;
    }
    document.getElementById('catalogo-resumo').textContent = 'Consultando o acervo...';
    try {
      renderizarLivros(await obterLivrosDaAPI());
    } catch (erro) {
      renderizarLivros([], true);
    }
  }

  function textoDeErroHTTP(resposta, tipo) {
    if (resposta.status === 404) return 'Livro não encontrado. Nenhuma alteração foi feita.';
    if (resposta.status === 409) return 'Conflito com os dados cadastrados. Nenhuma alteração foi confirmada.';
    if (resposta.status === 400 || resposta.status === 422) {
      return 'Dados rejeitados pelo servidor. Confira os campos e tente novamente.';
    }
    return `Não foi possível ${tipo} o livro (HTTP ${resposta.status}).`;
  }

  async function enviarPendencia(op) {
    if (!API_BASE_URL) return { estado: 'pendente', texto: 'Operação guardada localmente, aguardando a API.' };

    // Consultas são GET (sem efeitos no banco) e têm rotas distintas do CRUD.
    if (['consulta_autor', 'consulta_join', 'relatorio_genero', 'busca_catalogo', 'auditoria_estantes_vazias', 'analise_acervo_critico', 'listar_autores_unicos', 'buscar_livros_faixa_exemplares', 'relatorio_autores_multigenero'].includes(op.tipo)) {
      try {
        const base = API_BASE_URL.replace(/\/$/, '');
        const rotas = {
          consulta_autor: () => `${base}/livros/por-autor?autor=${encodeURIComponent(op.dados.autor)}`,
          consulta_join: () => `${base}/consultas/joins/${encodeURIComponent(op.dados.join)}`,
          relatorio_genero: () => `${base}/relatorios/estatisticas-por-genero?media_minima=${encodeURIComponent(op.dados.media_minima)}`,
          busca_catalogo: () => `${base}/catalogo/busca?termo=${encodeURIComponent(op.dados.termo)}`,
          auditoria_estantes_vazias: () => `${base}/auditoria/estantes-vazias`,
          analise_acervo_critico: () => `${base}/analises/acervo-critico?genero_alvo=${encodeURIComponent(op.dados.genero_alvo)}&genero_comparacao=${encodeURIComponent(op.dados.genero_comparacao)}`,
          listar_autores_unicos: () => `${base}/autores/unicos`,
          buscar_livros_faixa_exemplares: () => `${base}/livros/por-faixa?minimo=${encodeURIComponent(op.dados.minimo)}&maximo=${encodeURIComponent(op.dados.maximo)}`,
          relatorio_autores_multigenero: () => `${base}/relatorios/autores-multigenero?genero1=${encodeURIComponent(op.dados.genero1)}&genero2=${encodeURIComponent(op.dados.genero2)}`
        };
        const url = rotas[op.tipo]();
        const resposta = await fetch(url, { headers: { Accept: 'application/json' } });
        if (!resposta.ok) {
          return { estado: 'erro', texto: `A API não conseguiu executar a consulta (HTTP ${resposta.status}). A solicitação continua salva.` };
        }
        const dados = resposta.status === 204 ? [] : await resposta.json();
        // Se a resposta não for reconhecível, não remover a solicitação salva.
        if (op.tipo === 'consulta_autor') extrairResultadoAutor(dados, op.dados.autor);
        else if (op.tipo === 'consulta_join') extrairRegistrosJoin(dados);
        else if (op.tipo === 'relatorio_genero') extrairEstatisticasGenero(dados);
        else if (op.tipo === 'busca_catalogo') extrairResultadosCatalogo(dados);
        else if (op.tipo === 'auditoria_estantes_vazias') extrairEstantesVazias(dados);
        else if (op.tipo === 'analise_acervo_critico') extrairAcervoCritico(dados);
        else if (op.tipo === 'listar_autores_unicos') extrairAutoresUnicos(dados);
        else if (op.tipo === 'buscar_livros_faixa_exemplares') extrairLivrosFaixa(dados);
        else if (op.tipo === 'relatorio_autores_multigenero') extrairAutoresMultigenero(dados);
        retirarPendencia(op.chave);
        return { estado: 'sucesso', texto: 'Consulta concluída.', dados };
      } catch (erro) {
        return { estado: 'pendente', texto: 'A API não respondeu ou retornou dados incompatíveis. Consulta preservada neste navegador.' };
      }
    }
    const base = `${API_BASE_URL.replace(/\/$/, '')}/livros`;
    let url = base;
    let metodo = 'POST';
    let corpo = op.dados;
    try {
      if (op.tipo === 'cadastro_procedure') {
        url = `${base}/procedure`;
      }
      if (op.tipo === 'atualizacao') {
        url = `${base}/${encodeURIComponent(op.dados.id_livro)}`;
        metodo = 'PUT';
      }
      if (op.tipo === 'exclusao') {
        metodo = 'DELETE';
        corpo = undefined;
        let id = op.dados.identificador;
        if (op.dados.tipo_identificador === 'nome') {
          // O Python fornecido só apaga por ID: o nome precisa identificar UM livro.
          const livros = await obterLivrosDaAPI();
          const procurado = id.toLocaleLowerCase('pt-BR').trim();
          const encontrados = livros.filter((livro) => String(livro.nome ?? '').toLocaleLowerCase('pt-BR').trim() === procurado);
          if (encontrados.length !== 1 || encontrados[0].id_livro == null && encontrados[0].id == null) {
            retirarPendencia(op.chave);
            return {
              estado: 'erro',
              texto: encontrados.length > 1
                ? 'Há mais de um livro com esse nome. Use o ID para excluir com segurança.'
                : 'Nenhum livro com esse nome foi encontrado. Nenhum livro foi excluído.'
            };
          }
          id = encontrados[0].id_livro ?? encontrados[0].id;
        }
        url = `${base}/${encodeURIComponent(id)}`;
      }
      const resposta = await fetch(url, {
        method: metodo,
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        ...(corpo === undefined ? {} : { body: JSON.stringify(corpo) })
      });
      if (!resposta.ok) {
        retirarPendencia(op.chave);
        let msgServidor = '';
        try {
          const corpoErro = await resposta.json();
          if (corpoErro && typeof corpoErro.erro === 'string') msgServidor = corpoErro.erro;
        } catch (e) {}
        return {
          estado: 'erro',
          texto: msgServidor || textoDeErroHTTP(resposta, op.tipo === 'exclusao' ? 'excluir' : 'salvar')
        };
      }
      retirarPendencia(op.chave);
      return {
        estado: 'sucesso',
        texto: op.tipo === 'cadastro' ? 'Livro cadastrado com sucesso no banco de dados.'
          : op.tipo === 'cadastro_procedure' ? 'Livro cadastrado com sucesso via PROCEDURE.'
            : op.tipo === 'atualizacao' ? 'Livro atualizado com sucesso no banco de dados.'
              : 'Livro excluído com sucesso do banco de dados.' 
      };
    } catch (erro) {
      // Sem resposta do servidor, preserva a operação para uma próxima tentativa.
      return { estado: 'pendente', texto: 'Não foi possível contatar a API. A solicitação continua salva neste navegador.' };
    }
  }

  function obterDadosLivro(formulario, cadastro) {
    const dados = new FormData(formulario);
    const nome = String(dados.get('nome') || '').trim();
    const autor = String(dados.get('autor') || '').trim();
    const genero = String(dados.get('genero') || '').trim();
    const exemplares = Number(dados.get('numero_de_exemplares'));
    if (!nome || !autor || !genero || !Number.isSafeInteger(exemplares) || exemplares < 0) return null;
    const livro = {
      nome, autor, genero,
      numero_de_exemplares: exemplares,
      pode_ser_emprestado: dados.get('pode_ser_emprestado') === 'true'
    };
    if (cadastro) {
      const estante = Number(dados.get('id_estante'));
      if (!Number.isSafeInteger(estante) || estante < 1) return null;
      livro.id_estante = estante;
    } else {
      const id = Number(dados.get('id_livro'));
      if (!Number.isSafeInteger(id) || id < 1) return null;
      livro.id_livro = id;
    }
    return livro;
  }

  async function salvarFormulario(evento, tipo) {
    evento.preventDefault();
    const formulario = evento.currentTarget;
    let dados;
    if (tipo === 'exclusao') {
      const fd = new FormData(formulario);
      const tipoIdentificador = String(fd.get('tipo_identificador'));
      const identificador = String(fd.get('identificador') || '').trim();
      if (!identificador || (tipoIdentificador === 'id' &&
          (!/^[1-9]\d*$/.test(identificador) || !Number.isSafeInteger(Number(identificador))))) {
        mensagemFormulario(tipo, 'Informe um ID positivo válido ou um nome não vazio.', 'erro');
        return;
      }
      dados = { tipo_identificador: tipoIdentificador, identificador };
    } else {
      dados = obterDadosLivro(formulario, tipo === 'cadastro' || tipo === 'cadastro_procedure');
      if (!dados) {
        mensagemFormulario(tipo, 'Preencha corretamente todos os campos obrigatórios.', 'erro');
        return;
      }
    }
    const operacao = criarPendencia(tipo, dados);
    if (!operacao) {
      mensagemFormulario(tipo, 'Não foi possível salvar no navegador. Verifique se o armazenamento local está disponível.', 'erro');
      return;
    }
    formulario.reset();
    if (tipo === 'exclusao') atualizarTipoExclusao();
    mensagemFormulario(tipo, 'Dados salvos neste navegador para envio posterior. Nenhuma alteração foi feita no banco ainda.');

    if (API_BASE_URL) {
      const botao = formulario.querySelector('button[type="submit"]');
      botao.disabled = true;
      const resultado = await enviarPendencia(operacao);
      mensagemFormulario(tipo, resultado.texto, resultado.estado);
      if (tipo === 'cadastro' || tipo === 'cadastro_procedure') {
        carregarOpcoesEstantesNoSelect();
      }
      botao.disabled = false;
    }
  }

  function atualizarTipoExclusao() {
    const porNome = document.getElementById('exclusao-tipo').value === 'nome';
    const campo = document.getElementById('exclusao-valor');
    document.getElementById('exclusao-label').textContent = porNome
      ? 'Insira o nome do livro:' : 'Insira o ID do livro:';
    campo.value = '';
    campo.inputMode = porNome ? 'text' : 'numeric';
  }

  async function sincronizarPendencias() {
    if (!API_BASE_URL) return;
    const botao = document.getElementById('botao-sincronizar');
    botao.disabled = true;
    document.getElementById('catalogo-resumo').textContent = 'Enviando operações pendentes...';
    let concluidas = 0;
    let rejeitadas = 0;
    for (const op of lerPendencias()) {
      const resultado = await enviarPendencia(op);
      if (resultado.estado === 'sucesso') concluidas++;
      if (resultado.estado === 'erro') rejeitadas++;
    }
    await abrirListagem();
    const total = lerPendencias().length;
    document.getElementById('catalogo-resumo').textContent =
      `Sincronização: ${concluidas} concluída(s), ${rejeitadas} rejeitada(s), ${total} ainda pendente(s).`;
    botao.disabled = false;
  }

  /* ------------------------------------------------------------------------
     4. AÇÕES AVANÇADAS: FUNCTION, PROCEDURE E CONSULTAS COM JOIN
     ------------------------------------------------------------------------ */
  let cadastroViaProcedure = false;
  const JOINS = Object.freeze({
    natural: { titulo: 'Natural Join', tabelas: ['livros', 'estantes'] },
    inner:   { titulo: 'Inner Join', tabelas: ['estantes', 'espacos'] },
    left:    { titulo: 'Left Outer Join', tabelas: ['espacos', 'estantes'] },
    right:   { titulo: 'Right Outer Join', tabelas: ['espacos', 'estantes'] },
    full:    { titulo: 'Full Outer Join', tabelas: ['espacos', 'estantes'] }
  });
  const NOMES_COLUNAS_JOIN = {
    nome: 'Livro', tipo: 'Tipo', id_estante: 'ID da estante', id_espaco: 'ID do espaço',
    numero_de_espacos: 'Número de espaços', dominio_lado_1: 'Domínio lado 1',
    dominio_lado_2: 'Domínio lado 2'
  };

  async function carregarOpcoesEstantesNoSelect() {
    const selectEstante = document.getElementById('cadastro-estante');
    const ajuda = document.getElementById('ajuda-estante-cadastro');
    if (!selectEstante) return;
    try {
      const base = API_BASE_URL.replace(/\/$/, '');
      const resp = await fetch(`${base}/estantes`, { headers: { Accept: 'application/json' } });
      if (!resp.ok) throw new Error('Falha ao buscar estantes');
      const estantes = await resp.json();
      selectEstante.innerHTML = '';
      if (!Array.isArray(estantes) || estantes.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'Nenhuma estante cadastrada — Crie uma em "Criar / Remover Estante"';
        selectEstante.appendChild(opt);
        if (ajuda) {
          ajuda.textContent = '⚠️ Não há estantes no banco! Clique no botão "Criar / Remover Estante" abaixo para criar uma estante primeiro.';
        }
        return;
      }
      for (const est of estantes) {
        const opt = document.createElement('option');
        opt.value = String(est.id_estante);
        const cap = Number(est.capacidade_livros ?? 100);
        const ocup = Number(est.exemplares_ocupados ?? 0);
        const vagas = Number(est.vagas_restantes ?? Math.max(0, cap - ocup));
        opt.textContent = `#${est.id_estante} · ${est.dominio_lado_1} / ${est.dominio_lado_2} (${ocup}/${cap} · ${vagas} livres)`;
        selectEstante.appendChild(opt);
      }
      if (ajuda) {
        ajuda.textContent = `${estantes.length} estante(s) disponível(is) no banco de dados.`;
      }
    } catch (erro) {
      selectEstante.innerHTML = '<option value="">Erro ao carregar estantes da API</option>';
    }
  }

  function abrirCadastro(viaProcedure) {
    cadastroViaProcedure = viaProcedure;
    const tituloCadastro = document.getElementById('titulo-cadastro');
    tituloCadastro.textContent = viaProcedure
      ? 'Cadastrar livro via PROCEDURE' : 'Cadastrar novo livro';
    tituloCadastro.classList.toggle('titulo-cadastro--procedure', viaProcedure);
    mensagemFormulario('cadastro', '');
    carregarOpcoesEstantesNoSelect();
    mostrarTela('cadastro');
  }

  function extrairResultadoAutor(dados, autor) {
    let livros = null;
    let total = null;
    if (Array.isArray(dados)) {
      livros = dados;
    } else if (typeof dados === 'number') {
      total = dados;
    } else if (dados && typeof dados === 'object') {
      if (Array.isArray(dados.livros)) livros = dados.livros;
      else if (Array.isArray(dados.data)) livros = dados.data;
      else if (Array.isArray(dados.registros)) livros = dados.registros;
      const contagem = dados.total ?? dados.total_livros ?? dados.quantidade;
      if (contagem !== undefined && contagem !== null) total = Number(contagem);
    }
    if (livros !== null) {
      // Mesmo que a API entregue registros extras, nunca exibir outro autor.
      const filtro = autor.toLocaleLowerCase('pt-BR').trim();
      livros = livros.filter((livro) => livro && typeof livro === 'object' &&
        String(livro.autor ?? '').toLocaleLowerCase('pt-BR').includes(filtro));
      if (total === null) total = livros.length;
    }
    if (!Number.isSafeInteger(total) || total < 0) {
      throw new Error('A resposta da FUNCTION não contém uma contagem válida.');
    }
    return { total, livros };
  }

  function apresentarAutor(autor, dados) {
    const { total, livros } = extrairResultadoAutor(dados, autor);
    const resumo = document.getElementById('resumo-autor');
    resumo.textContent = `Autor pesquisado: ${autor} — ${total} livro(s) encontrado(s).`;
    const recipiente = document.getElementById('lista-autor');
    if (total === 0) {
      mostrarEstado(recipiente, 'Nenhum livro encontrado.', `Não há livros cadastrados para o autor pesquisado: ${autor}.`);
    } else if (livros === null) {
      mostrarEstado(recipiente, `${total} livro(s) registrado(s)`,
        'A FUNCTION retornou a quantidade. Para apresentar os cartões, a futura API também deve devolver a lista desses livros.');
    } else if (!livros.length) {
      mostrarEstado(recipiente, 'Nenhum registro detalhado', 'A API não retornou livros deste autor, apesar de informar uma quantidade maior que zero.');
    } else {
      preencherFichasLivro(recipiente, livros);
    }
  }

  async function consultarAutor(evento) {
    evento.preventDefault();
    const formulario = evento.currentTarget;
    const autor = String(new FormData(formulario).get('autor') || '').trim();
    if (!autor) {
      document.getElementById('resumo-autor').textContent = 'Informe o nome de um autor para realizar a pesquisa.';
      document.getElementById('autor-nome').focus();
      return;
    }
    const recipiente = document.getElementById('lista-autor');
    const resumo = document.getElementById('resumo-autor');
    const operacao = criarPendencia('consulta_autor', { autor, recurso: 'fn_contar_livros_por_autor' });
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar esta pesquisa no navegador.';
      return;
    }
    mostrarEstado(recipiente, 'Pesquisa preparada',
      'O nome do autor foi salvo neste navegador. A pesquisa será executada quando a API estiver disponível.');
    resumo.textContent = `Autor: ${autor} — consulta pendente, sem acesso ao banco.`;
    if (!API_BASE_URL) return;
    const botao = document.getElementById('botao-buscar-autor');
    botao.disabled = true;
    resumo.textContent = `Buscando livros de ${autor}...`;
    const resultado = await enviarPendencia(operacao);
    if (resultado.estado === 'sucesso') {
      apresentarAutor(autor, resultado.dados);
    } else {
      resumo.textContent = resultado.texto;
      mostrarEstado(recipiente, 'Pesquisa não concluída', 'A solicitação permanece guardada para uma nova tentativa.');
    }
    botao.disabled = false;
  }

  function extrairRegistrosJoin(dados) {
    if (Array.isArray(dados)) return dados;
    if (dados && typeof dados === 'object') {
      if (Array.isArray(dados.registros)) return dados.registros;
      if (Array.isArray(dados.data)) return dados.data;
      if (Array.isArray(dados.resultados)) return dados.resultados;
    }
    throw new Error('A resposta da consulta JOIN não contém uma lista de registros.');
  }

  function apresentarJoin(dados) {
    const linhas = extrairRegistrosJoin(dados);
    const recipiente = document.getElementById('lista-join');
    document.getElementById('resumo-join').textContent = linhas.length === 1
      ? '1 registro retornado pela consulta.'
      : `${linhas.length} registros retornados pela consulta.`;
    if (!linhas.length) {
      mostrarEstado(recipiente, 'Nenhum resultado encontrado.', 'A consulta foi executada, mas não retornou registros.');
      return;
    }
    const fragmento = document.createDocumentFragment();
    linhas.forEach((linha) => {
      const ficha = document.createElement('article');
      ficha.className = 'ficha-livro ficha-join';
      const detalhes = document.createElement('dl');
      if (linha && typeof linha === 'object' && !Array.isArray(linha)) {
        Object.entries(linha).forEach(([chave, valor]) => {
          const campo = document.createElement('div');
          const nome = document.createElement('dt');
          nome.textContent = `${NOMES_COLUNAS_JOIN[chave] ?? chave.replace(/_/g, ' ')}:`;
          const conteudo = document.createElement('dd');
          conteudo.textContent = valor == null ? '—' : String(valor);
          campo.append(nome, conteudo);
          detalhes.append(campo);
        });
      }
      ficha.append(detalhes);
      fragmento.append(ficha);
    });
    recipiente.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  async function executarJoin(codigo) {
    if (!Object.prototype.hasOwnProperty.call(JOINS, codigo)) return;
    const join = JOINS[codigo];
    document.getElementById('titulo-join-resultado').textContent = join.titulo;
    const operacao = criarPendencia('consulta_join', {
      join: codigo,
      tabelas: [...join.tabelas],
      operacao: `${join.titulo.toUpperCase()} (${join.tabelas.join(' x ')})`
    });
    mostrarTela('resultadoJoin');
    const resumo = document.getElementById('resumo-join');
    const recipiente = document.getElementById('lista-join');
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar a consulta no navegador.';
      mostrarEstado(recipiente, 'Armazenamento indisponível', 'Verifique o armazenamento local do navegador.');
      return;
    }
    resumo.textContent = `${join.titulo} — ${join.tabelas.join(' × ')}.`;
    mostrarEstado(recipiente, 'Consulta preparada',
      'A JOIN selecionada foi salva neste navegador e aguarda a futura API. Nenhuma consulta foi executada no banco ainda.');
    if (!API_BASE_URL) return;
    resumo.textContent = `Executando ${join.titulo}...`;
    const resultado = await enviarPendencia(operacao);
    if (resultado.estado === 'sucesso') apresentarJoin(resultado.dados);
    else {
      resumo.textContent = resultado.texto;
      mostrarEstado(recipiente, 'Consulta não concluída', 'A solicitação continua salva neste navegador.');
    }
  }

  /* ------------------------------------------------------------------------
     5. RELATÓRIO GERENCIAL E BUSCA DO CATÁLOGO
     Relatório: cada registro é um GÊNERO, não um livro (AVG, MIN, MAX, HAVING).
     Busca: cada registro traz SOMENTE as quatro colunas do SELECT em Python.
     ------------------------------------------------------------------------ */
  const formatoNumero = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2, minimumFractionDigits: 2 });

  function extrairListaConsulta(dados, descricao) {
    if (Array.isArray(dados)) return dados;
    if (dados && typeof dados === 'object') {
      for (const chave of ['registros', 'resultados', 'dados', 'data']) {
        if (Array.isArray(dados[chave])) return dados[chave];
      }
    }
    throw new Error(`A resposta da API para ${descricao} não contém uma lista de registros.`);
  }

  function extrairEstatisticasGenero(dados) {
    const linhas = extrairListaConsulta(dados, 'estatísticas por gênero');
    return linhas.map((linha) => {
      if (!linha || Array.isArray(linha) || typeof linha !== 'object') throw new Error('Linha inválida no relatório.');
      const genero = linha.genero ?? linha.GENERO;
      const media = Number(linha.media_exemplares ?? linha.MEDIA_EXEMPLARES);
      const minimo = Number(linha.minimo_exemplares ?? linha.MINIMO_EXEMPLARES);
      const maximo = Number(linha.maximo_exemplares ?? linha.MAXIMO_EXEMPLARES);
      if (genero == null || !Number.isFinite(media) || !Number.isSafeInteger(minimo) ||
          !Number.isSafeInteger(maximo) || minimo < 0 || maximo < minimo) {
        throw new Error('A API devolveu estatísticas inválidas para um gênero.');
      }
      return { genero: String(genero), media, minimo, maximo };
    });
  }

  function extrairResultadosCatalogo(dados) {
    const linhas = extrairListaConsulta(dados, 'busca no catálogo');
    return linhas.map((linha) => {
      if (!linha || Array.isArray(linha) || typeof linha !== 'object') throw new Error('Linha inválida da busca.');
      const titulo = linha.titulo_destaque ?? linha.TITULO_DESTAQUE;
      const catalogo = linha.catalogo_completo ?? linha.CATALOGO_COMPLETO;
      const genero = linha.genero_curto ?? linha.GENERO_CURTO;
      const tamanho = Number(linha.tamanho_titulo ?? linha.TAMANHO_TITULO);
      if (titulo == null || catalogo == null || !Number.isSafeInteger(tamanho) || tamanho < 0) {
        throw new Error('A API devolveu uma obra sem os campos obrigatórios.');
      }
      return {
        titulo: String(titulo),
        catalogo: String(catalogo),
        genero: genero == null ? 'Não informado' : String(genero),
        tamanho
      };
    });
  }

  function criarLinhaDetalhe(rotulo, valor) {
    const item = document.createElement('div');
    const nome = document.createElement('dt');
    const dado = document.createElement('dd');
    nome.textContent = rotulo;
    dado.textContent = String(valor);
    item.append(nome, dado);
    return item;
  }

  function mostrarRelatorioGenero(dados, mediaMinima) {
    const registros = extrairEstatisticasGenero(dados);
    const lista = document.getElementById('lista-relatorio-genero');
    document.getElementById('resumo-relatorio-genero').textContent =
      `${registros.length} gênero(s) com média superior a ${formatoNumero.format(mediaMinima)} exemplares por livro.`;
    if (!registros.length) {
      mostrarEstado(lista, 'Nenhum gênero atende ao filtro',
        'A consulta foi concluída, mas nenhum gênero possui média de exemplares maior que o valor informado.');
      return;
    }
    const fragmento = document.createDocumentFragment();
    for (const registro of registros) {
      const ficha = document.createElement('article');
      ficha.className = 'ficha-livro ficha-genero';
      const titulo = document.createElement('h2');
      titulo.textContent = registro.genero;
      const metricas = document.createElement('dl');
      metricas.className = 'ficha-genero__metricas';
      for (const [rotulo, valor] of [
        ['Média', formatoNumero.format(registro.media)],
        ['Mínimo', registro.minimo],
        ['Máximo', registro.maximo]
      ]) {
        const item = criarLinhaDetalhe(rotulo, valor);
        item.className = 'ficha-genero__metrica';
        metricas.append(item);
      }
      ficha.append(titulo, metricas);
      fragmento.append(ficha);
    }
    lista.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  function mostrarBuscaCatalogo(dados, termo) {
    const registros = extrairResultadosCatalogo(dados);
    const lista = document.getElementById('lista-busca-catalogo');
    document.getElementById('resumo-busca-catalogo').textContent =
      `${registros.length} obra(s) encontrada(s) para “${termo}”.`;
    if (!registros.length) {
      mostrarEstado(lista, 'Nenhuma obra encontrada',
        'Não há livros cujo título ou nome do autor corresponda ao termo pesquisado.');
      return;
    }
    const fragmento = document.createDocumentFragment();
    for (const registro of registros) {
      const ficha = document.createElement('article');
      ficha.className = 'ficha-livro ficha-catalogo-busca';
      const rotulo = document.createElement('p');
      rotulo.className = 'ficha-catalogo-busca__rotulo';
      rotulo.textContent = 'Título em destaque';
      const titulo = document.createElement('h2');
      titulo.textContent = registro.titulo;
      const detalhes = document.createElement('dl');
      detalhes.append(
        criarLinhaDetalhe('Catálogo:', registro.catalogo),
        criarLinhaDetalhe('Gênero (resumo):', registro.genero),
        criarLinhaDetalhe('Caracteres no título:', registro.tamanho)
      );
      ficha.append(rotulo, titulo, detalhes);
      fragmento.append(ficha);
    }
    lista.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  async function consultarRelatorioGenero(evento) {
    evento.preventDefault();
    const campo = document.getElementById('media-minima-genero');
    const valor = campo.value.trim();
    const mediaMinima = Number(valor);
    const resumo = document.getElementById('resumo-relatorio-genero');
    const lista = document.getElementById('lista-relatorio-genero');
    if (!valor || !Number.isFinite(mediaMinima) || mediaMinima < 0) {
      resumo.textContent = 'Informe uma média mínima válida (zero ou um número positivo).';
      campo.focus();
      return;
    }
    const operacao = criarPendencia('relatorio_genero', {
      media_minima: mediaMinima,
      recurso: 'relatorio_estatisticas_genero'
    });
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar o filtro neste navegador.';
      mostrarEstado(lista, 'Armazenamento indisponível', 'Verifique as permissões de armazenamento local.');
      return;
    }
    resumo.textContent = `Filtro: média maior que ${formatoNumero.format(mediaMinima)} — relatório pendente.`;
    mostrarEstado(lista, 'Relatório preparado',
      'O filtro foi salvo neste navegador. Nenhum gênero foi consultado no banco de dados ainda.');
    if (!API_BASE_URL) return;
    const botao = document.getElementById('botao-relatorio-genero');
    botao.disabled = true;
    resumo.textContent = 'Gerando relatório por gênero...';
    const resultado = await enviarPendencia(operacao);
    if (resultado.estado === 'sucesso') mostrarRelatorioGenero(resultado.dados, mediaMinima);
    else {
      resumo.textContent = resultado.texto;
      mostrarEstado(lista, 'Relatório não concluído', 'O filtro permanece salvo para tentar novamente.');
    }
    botao.disabled = false;
  }

  async function buscarCatalogoPalavraChave(evento) {
    evento.preventDefault();
    const campo = document.getElementById('termo-catalogo');
    const termo = campo.value.trim();
    const resumo = document.getElementById('resumo-busca-catalogo');
    const lista = document.getElementById('lista-busca-catalogo');
    if (!termo) {
      resumo.textContent = 'Informe uma palavra-chave para pesquisar o catálogo.';
      campo.focus();
      return;
    }
    const operacao = criarPendencia('busca_catalogo', {
      termo,
      recurso: 'buscar_catalogo_palavra_chave'
    });
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar a palavra-chave neste navegador.';
      mostrarEstado(lista, 'Armazenamento indisponível', 'Verifique as permissões de armazenamento local.');
      return;
    }
    resumo.textContent = `Palavra-chave: “${termo}” — busca pendente.`;
    mostrarEstado(lista, 'Pesquisa preparada',
      'A palavra-chave foi salva neste navegador. Nenhuma obra foi consultada no banco de dados ainda.');
    if (!API_BASE_URL) return;
    const botao = document.getElementById('botao-busca-catalogo');
    botao.disabled = true;
    resumo.textContent = `Pesquisando obras com “${termo}”...`;
    const resultado = await enviarPendencia(operacao);
    if (resultado.estado === 'sucesso') mostrarBuscaCatalogo(resultado.dados, termo);
    else {
      resumo.textContent = resultado.texto;
      mostrarEstado(lista, 'Pesquisa não concluída', 'A palavra-chave continua salva para uma nova tentativa.');
    }
    botao.disabled = false;
  }

  /* ------------------------------------------------------------------------
     6. AUDITORIA DE ESTANTES, ANÁLISE CRÍTICA E AUTORES ÚNICOS
     Não há resultados fictícios: sem API, as solicitações ficam pendentes.
     ------------------------------------------------------------------------ */
  function extrairEstantesVazias(dados) {
    const linhas = extrairListaConsulta(dados, 'estantes vazias');
    return linhas.map((linha) => {
      if (!linha || typeof linha !== 'object' || Array.isArray(linha)) throw new Error('Estante retornada em formato inválido.');
      const id = Number(linha.id_estante ?? linha.ID_ESTANTE);
      const dominio = linha.dominio_lado_1 ?? linha.DOMINIO_LADO_1;
      if (!Number.isSafeInteger(id) || id <= 0) throw new Error('ID de estante inválido na resposta da API.');
      return { id, dominio: dominio == null ? 'Não informado' : String(dominio) };
    });
  }

  function mostrarEstantesVazias(dados) {
    const estantes = extrairEstantesVazias(dados);
    const lista = document.getElementById('lista-estantes-vazias');
    document.getElementById('resumo-estantes-vazias').textContent = estantes.length === 1
      ? 'Auditoria concluída: 1 estante sem livros.'
      : `Auditoria concluída: ${estantes.length} estantes sem livros.`;
    if (!estantes.length) {
      mostrarEstado(lista, 'Todas as estantes possuem livros',
        'A auditoria foi concluída: nenhuma estante vazia foi encontrada no banco de dados.');
      return;
    }
    const fragmento = document.createDocumentFragment();
    for (const estante of estantes) {
      const ficha = document.createElement('article');
      ficha.className = 'ficha-livro ficha-estante';
      const titulo = document.createElement('h2');
      titulo.textContent = `Estante nº ${estante.id}`;
      const detalhes = document.createElement('dl');
      detalhes.append(criarLinhaDetalhe('ID da estante:', estante.id), criarLinhaDetalhe('Domínio (lado 1):', estante.dominio));
      ficha.append(titulo, detalhes);
      fragmento.append(ficha);
    }
    lista.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  async function consultarEstantesVazias() {
    mostrarTela('estantesVazias');
    const lista = document.getElementById('lista-estantes-vazias');
    const resumo = document.getElementById('resumo-estantes-vazias');
    const operacao = criarPendencia('auditoria_estantes_vazias', { recurso: 'auditoria_estantes_vazias' });
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar a solicitação de auditoria.';
      mostrarEstado(lista, 'Armazenamento indisponível', 'Verifique as permissões de armazenamento local.');
      return;
    }
    resumo.textContent = 'Auditoria de estantes — aguardando integração com a API.';
    mostrarEstado(lista, 'Auditoria preparada',
      'O pedido para listar as estantes vazias foi salvo. O banco de dados ainda não foi consultado.');
    if (!API_BASE_URL) return;
    resumo.textContent = 'Consultando estantes vazias...';
    const resultado = await enviarPendencia(operacao);
    if (resultado.estado === 'sucesso') mostrarEstantesVazias(resultado.dados);
    else {
      resumo.textContent = resultado.texto;
      mostrarEstado(lista, 'Auditoria não concluída', 'A solicitação permanece salva neste navegador.');
    }
  }

  function extrairAcervoCritico(dados) {
    const linhas = extrairListaConsulta(dados, 'análise de acervo crítico');
    return linhas.map((linha) => {
      if (!linha || typeof linha !== 'object' || Array.isArray(linha)) throw new Error('Livro retornado em formato inválido.');
      const nome = linha.nome ?? linha.NOME;
      const total = Number(linha.numero_de_exemplares ?? linha.NUMERO_DE_EXEMPLARES);
      if (typeof nome !== 'string' || !nome.trim() || !Number.isSafeInteger(total) || total < 0) {
        throw new Error('Dados de livro inválidos na resposta da análise crítica.');
      }
      return { nome, total };
    });
  }

  function mostrarAcervoCritico(dados) {
    const livros = extrairAcervoCritico(dados);
    const lista = document.getElementById('lista-acervo-critico');
    document.getElementById('resumo-acervo-critico').textContent = livros.length === 1
      ? 'Análise concluída: 1 obra atende aos parâmetros.'
      : `Análise concluída: ${livros.length} obras atendem aos parâmetros.`;
    if (!livros.length) {
      mostrarEstado(lista, 'Nenhuma obra encontrada',
        'Não há obras nas estantes selecionadas com mais exemplares do que pelo menos um livro do gênero de comparação.');
      return;
    }
    const fragmento = document.createDocumentFragment();
    for (const livro of livros) {
      const ficha = document.createElement('article');
      ficha.className = 'ficha-livro ficha-acervo-critico';
      const titulo = document.createElement('h2');
      titulo.textContent = livro.nome;
      const detalhes = document.createElement('dl');
      detalhes.append(criarLinhaDetalhe('Nº de exemplares:', livro.total));
      ficha.append(titulo, detalhes);
      fragmento.append(ficha);
    }
    lista.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  async function consultarAcervoCritico(evento) {
    evento.preventDefault();
    const dominioCampo = document.getElementById('acervo-genero-alvo');
    const generoCampo = document.getElementById('acervo-genero-comparacao');
    const dominio = dominioCampo.value.trim();
    const genero = generoCampo.value.trim();
    const resumo = document.getElementById('resumo-acervo-critico');
    const lista = document.getElementById('lista-acervo-critico');
    if (!dominio || !genero) {
      resumo.textContent = 'Informe o domínio da estante e o gênero de comparação.';
      (!dominio ? dominioCampo : generoCampo).focus();
      return;
    }
    const operacao = criarPendencia('analise_acervo_critico', {
      genero_alvo: dominio,
      genero_comparacao: genero,
      recurso: 'analise_acervo_critico'
    });
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar os parâmetros desta análise.';
      mostrarEstado(lista, 'Armazenamento indisponível', 'Verifique as permissões de armazenamento local.');
      return;
    }
    resumo.textContent = `Domínio: “${dominio}” · Gênero comparado: “${genero}” — análise pendente.`;
    mostrarEstado(lista, 'Análise preparada',
      'Os dois filtros foram salvos neste navegador. Nenhum livro foi consultado no banco ainda.');
    if (!API_BASE_URL) return;
    resumo.textContent = 'Analisando o acervo...';
    const botao = document.getElementById('botao-acervo-critico');
    botao.disabled = true;
    const resultado = await enviarPendencia(operacao);
    if (resultado.estado === 'sucesso') mostrarAcervoCritico(resultado.dados);
    else {
      resumo.textContent = resultado.texto;
      mostrarEstado(lista, 'Análise não concluída', 'Os filtros permanecem salvos neste navegador.');
    }
    botao.disabled = false;
  }

  function extrairAutoresUnicos(dados) {
    const linhas = extrairListaConsulta(dados, 'autores únicos');
    return linhas.map((linha) => {
      const autor = typeof linha === 'string' ? linha
        : linha && typeof linha === 'object' && !Array.isArray(linha) ? (linha.autor ?? linha.AUTOR) : null;
      if (typeof autor !== 'string' || !autor.trim()) throw new Error('Nome de autor inválido na resposta da API.');
      return autor;
    });
  }

  function mostrarAutoresUnicos(dados) {
    const autores = extrairAutoresUnicos(dados);
    const lista = document.getElementById('lista-autores-unicos');
    document.getElementById('resumo-autores-unicos').textContent = autores.length === 1
      ? '1 autor distinto cadastrado no catálogo.'
      : `${autores.length} autores distintos cadastrados no catálogo.`;
    if (!autores.length) {
      mostrarEstado(lista, 'Nenhum autor encontrado',
        'A consulta foi concluída e não há autores cadastrados nos livros do banco.');
      return;
    }
    const fragmento = document.createDocumentFragment();
    for (const autor of autores) {
      const ficha = document.createElement('article');
      ficha.className = 'ficha-livro ficha-autor-unico';
      const icone = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      icone.setAttribute('class', 'icone ficha-autor-unico__icone');
      icone.setAttribute('aria-hidden', 'true');
      const uso = document.createElementNS('http://www.w3.org/2000/svg', 'use');
      uso.setAttribute('href', '#i-usuario');
      icone.append(uso);
      const titulo = document.createElement('h2');
      titulo.textContent = autor;
      ficha.append(icone, titulo);
      fragmento.append(ficha);
    }
    lista.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  async function consultarAutoresUnicos() {
    mostrarTela('autoresUnicos');
    const lista = document.getElementById('lista-autores-unicos');
    const resumo = document.getElementById('resumo-autores-unicos');
    const operacao = criarPendencia('listar_autores_unicos', { recurso: 'listar_autores_unicos' });
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar a lista solicitada.';
      mostrarEstado(lista, 'Armazenamento indisponível', 'Verifique as permissões de armazenamento local.');
      return;
    }
    resumo.textContent = 'Autores únicos — aguardando integração com a API.';
    mostrarEstado(lista, 'Consulta preparada',
      'O pedido para listar autores únicos foi salvo. A lista real virá do banco de dados quando a API estiver disponível.');
    if (!API_BASE_URL) return;
    resumo.textContent = 'Consultando autores únicos...';
    const resultado = await enviarPendencia(operacao);
    if (resultado.estado === 'sucesso') mostrarAutoresUnicos(resultado.dados);
    else {
      resumo.textContent = resultado.texto;
      mostrarEstado(lista, 'Consulta não concluída', 'A solicitação permanece salva neste navegador.');
    }
  }

  /* ------------------------------------------------------------------------
     6. ÚLTIMAS OPÇÕES AVANÇADAS: BETWEEN e INTERSECT
     O Python fornecido retorna três colunas na faixa de exemplares e somente
     o nome do autor no INTERSECT; não criar campos que o SQL não disponibiliza.
     ------------------------------------------------------------------------ */
  function extrairLivrosFaixa(dados) {
    const linhas = extrairListaConsulta(dados, 'livros por faixa de exemplares');
    return linhas.map((linha) => {
      if (!linha || typeof linha !== 'object' || Array.isArray(linha)) {
        throw new Error('Livro retornado em formato inválido na busca por faixa.');
      }
      const nome = linha.nome ?? linha.NOME;
      const autor = linha.autor ?? linha.AUTOR;
      const exemplares = Number(linha.numero_de_exemplares ?? linha.NUMERO_DE_EXEMPLARES);
      if (typeof nome !== 'string' || !nome.trim() || typeof autor !== 'string' || !autor.trim() ||
          !Number.isSafeInteger(exemplares) || exemplares < 0) {
        throw new Error('A API devolveu um livro com dados inválidos para a busca por faixa.');
      }
      return { nome, autor, exemplares };
    });
  }

  function mostrarLivrosFaixa(dados, minimo, maximo) {
    const livros = extrairLivrosFaixa(dados);
    const lista = document.getElementById('lista-faixa-exemplares');
    const resumo = document.getElementById('resumo-faixa-exemplares');
    resumo.textContent = livros.length === 1
      ? `1 livro encontrado com ${minimo} a ${maximo} exemplares (inclusive).`
      : `${livros.length} livros encontrados com ${minimo} a ${maximo} exemplares (inclusive).`;
    if (!livros.length) {
      mostrarEstado(lista, 'Nenhum livro encontrado',
        'Não há livros cadastrados com uma quantidade de exemplares dentro dessa faixa.');
      return;
    }
    const fragmento = document.createDocumentFragment();
    for (const livro of livros) {
      const ficha = document.createElement('article');
      ficha.className = 'ficha-livro ficha-faixa';
      const titulo = document.createElement('h2');
      titulo.textContent = livro.nome;
      const detalhes = document.createElement('dl');
      detalhes.append(
        criarLinhaDetalhe('Autor(a):', livro.autor),
        criarLinhaDetalhe('Nº de exemplares:', livro.exemplares)
      );
      ficha.append(titulo, detalhes);
      fragmento.append(ficha);
    }
    lista.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  async function buscarLivrosPorFaixa(evento) {
    evento.preventDefault();
    const campoMinimo = document.getElementById('faixa-minimo');
    const campoMaximo = document.getElementById('faixa-maximo');
    const minimo = Number(campoMinimo.value);
    const maximo = Number(campoMaximo.value);
    const resumo = document.getElementById('resumo-faixa-exemplares');
    const lista = document.getElementById('lista-faixa-exemplares');
    if (!campoMinimo.value || !Number.isSafeInteger(minimo) || minimo < 0) {
      resumo.textContent = 'Informe um número mínimo de exemplares válido (inteiro não negativo).';
      campoMinimo.focus();
      return;
    }
    if (!campoMaximo.value || !Number.isSafeInteger(maximo) || maximo < 0) {
      resumo.textContent = 'Informe um número máximo de exemplares válido (inteiro não negativo).';
      campoMaximo.focus();
      return;
    }
    if (minimo > maximo) {
      resumo.textContent = 'O mínimo não pode ser maior que o máximo.';
      campoMaximo.setCustomValidity('O máximo deve ser maior ou igual ao mínimo.');
      campoMaximo.reportValidity();
      campoMaximo.setCustomValidity('');
      campoMaximo.focus();
      return;
    }
    const operacao = criarPendencia('buscar_livros_faixa_exemplares', {
      minimo, maximo, recurso: 'buscar_livros_por_faixa_exemplares'
    });
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar esta pesquisa no navegador.';
      mostrarEstado(lista, 'Armazenamento indisponível', 'Verifique as permissões de armazenamento local.');
      return;
    }
    resumo.textContent = `Faixa de ${minimo} a ${maximo} exemplares — aguardando integração com a API.`;
    mostrarEstado(lista, 'Pesquisa preparada',
      'Os limites foram salvos neste navegador. Nenhuma consulta foi executada no banco de dados.');
    if (!API_BASE_URL) return;
    resumo.textContent = `Buscando obras com ${minimo} a ${maximo} exemplares...`;
    const botao = document.getElementById('botao-faixa-exemplares');
    botao.disabled = true;
    try {
      const resultado = await enviarPendencia(operacao);
      if (resultado.estado === 'sucesso') mostrarLivrosFaixa(resultado.dados, minimo, maximo);
      else {
        resumo.textContent = resultado.texto;
        mostrarEstado(lista, 'Pesquisa não concluída', 'Os limites permanecem salvos neste navegador.');
      }
    } finally {
      botao.disabled = false;
    }
  }

  function extrairAutoresMultigenero(dados) {
    const linhas = extrairListaConsulta(dados, 'autores multigênero');
    return linhas.map((linha) => {
      const autor = typeof linha === 'string' ? linha
        : linha && typeof linha === 'object' && !Array.isArray(linha) ? (linha.autor ?? linha.AUTOR) : null;
      if (typeof autor !== 'string' || !autor.trim()) {
        throw new Error('A API devolveu um autor inválido no relatório multigênero.');
      }
      return autor;
    });
  }

  function mostrarAutoresMultigenero(dados, genero1, genero2) {
    const autores = extrairAutoresMultigenero(dados);
    const lista = document.getElementById('lista-autores-multigenero');
    const resumo = document.getElementById('resumo-autores-multigenero');
    resumo.textContent = autores.length === 1
      ? `1 autor encontrado em ambos os gêneros: “${genero1}” e “${genero2}”.`
      : `${autores.length} autores encontrados em ambos os gêneros: “${genero1}” e “${genero2}”.`;
    if (!autores.length) {
      mostrarEstado(lista, 'Nenhum autor em comum',
        `Não foram encontrados autores com livros nos dois gêneros informados: “${genero1}” e “${genero2}”.`);
      return;
    }
    const fragmento = document.createDocumentFragment();
    for (const autor of autores) {
      const ficha = document.createElement('article');
      ficha.className = 'ficha-livro ficha-autor-unico ficha-autor-multigenero';
      const icone = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      icone.setAttribute('class', 'icone ficha-autor-unico__icone');
      icone.setAttribute('aria-hidden', 'true');
      const uso = document.createElementNS('http://www.w3.org/2000/svg', 'use');
      uso.setAttribute('href', '#i-cruzar');
      icone.append(uso);
      const titulo = document.createElement('h2');
      titulo.textContent = autor;
      ficha.append(icone, titulo);
      fragmento.append(ficha);
    }
    lista.replaceChildren(fragmento);
    atualizarSliders();
    requestAnimationFrame(atualizarSliders);
  }

  async function consultarAutoresMultigenero(evento) {
    evento.preventDefault();
    const campoGenero1 = document.getElementById('multigenero-genero1');
    const campoGenero2 = document.getElementById('multigenero-genero2');
    const genero1 = campoGenero1.value.trim();
    const genero2 = campoGenero2.value.trim();
    const resumo = document.getElementById('resumo-autores-multigenero');
    const lista = document.getElementById('lista-autores-multigenero');
    if (!genero1 || !genero2) {
      resumo.textContent = 'Preencha os dois gêneros que deseja comparar.';
      (!genero1 ? campoGenero1 : campoGenero2).focus();
      return;
    }
    const operacao = criarPendencia('relatorio_autores_multigenero', {
      genero1, genero2, recurso: 'relatorio_autores_multigenero'
    });
    if (!operacao) {
      resumo.textContent = 'Não foi possível guardar os gêneros no navegador.';
      mostrarEstado(lista, 'Armazenamento indisponível', 'Verifique as permissões de armazenamento local.');
      return;
    }
    resumo.textContent = `Gêneros “${genero1}” e “${genero2}” — aguardando integração com a API.`;
    mostrarEstado(lista, 'Relatório preparado',
      'Os dois gêneros foram salvos neste navegador. Nenhuma consulta foi executada no banco de dados.');
    if (!API_BASE_URL) return;
    resumo.textContent = 'Consultando autores em comum...';
    const botao = document.getElementById('botao-autores-multigenero');
    botao.disabled = true;
    try {
      const resultado = await enviarPendencia(operacao);
      if (resultado.estado === 'sucesso') mostrarAutoresMultigenero(resultado.dados, genero1, genero2);
      else {
        resumo.textContent = resultado.texto;
        mostrarEstado(lista, 'Relatório não concluído', 'Os gêneros permanecem salvos neste navegador.');
      }
    } finally {
      botao.disabled = false;
    }
  }

  /* ------------------------------------------------------------------------
     GERENCIAMENTO DE ESTANTES (CRIAR, LISTAR E EXCLUIR COM ALERTA CASCADE)
     ------------------------------------------------------------------------ */
  async function carregarTelaGerenciarEstantes() {
    mostrarTela('estantes');
    const lista = document.getElementById('lista-gerenciar-estantes');
    const resumo = document.getElementById('resumo-gerenciar-estantes');
    mostrarEstado(lista, 'Consultando estantes...', 'Buscando estantes cadastradas no PostgreSQL...');
    try {
      const base = API_BASE_URL.replace(/\/$/, '');
      const resp = await fetch(`${base}/estantes`, { headers: { Accept: 'application/json' } });
      if (!resp.ok) throw new Error('Falha ao listar estantes');
      const estantes = await resp.json();
      if (!Array.isArray(estantes) || estantes.length === 0) {
        resumo.textContent = 'Nenhuma estante cadastrada no momento. Preencha os campos acima para criar a primeira estante!';
        mostrarEstado(lista, 'Nenhuma estante cadastrada', 'Use o formulário acima ("+ Criar Nova Estante") para adicionar estantes à biblioteca.');
        return;
      }
      resumo.textContent = `${estantes.length} estante(s) cadastrada(s). ⚠️ Atenção: Apagar uma estante removerá TODOS os livros guardados nela!`;
      const fragmento = document.createDocumentFragment();
      for (const est of estantes) {
        const ficha = document.createElement('article');
        ficha.className = 'ficha-livro';
        const qtdLivros = Number(est.qtd_livros_cadastrados || 0);
        const cap = Number(est.capacidade_livros ?? 100);
        const ocup = Number(est.exemplares_ocupados ?? 0);
        const vagas = Number(est.vagas_restantes ?? Math.max(0, cap - ocup));
        ficha.innerHTML = `
          <dl>
            <div><dt>Domínio Lado 1:</dt><dd>${est.dominio_lado_1 || '—'}</dd></div>
            <div><dt>Domínio Lado 2:</dt><dd>${est.dominio_lado_2 || '—'}</dd></div>
            <div><dt>Capacidade máxima:</dt><dd>${cap} exemplar(es)</dd></div>
            <div><dt>Ocupação atual:</dt><dd><strong>${ocup} / ${cap} exemplar(es) (${vagas} vaga(s) livre(s)) — ${qtdLivros} título(s)</strong></dd></div>
          </dl>
          <div class="ficha-estante-rodape">
            <span class="ficha-livro__id">Estante #${est.id_estante}</span>
            <button type="button" class="botao botao--perigo botao--compacto" data-excluir-estante="${est.id_estante}" data-tema-estante="${est.dominio_lado_1} / ${est.dominio_lado_2}" data-qtd-livros="${qtdLivros}">
              Excluir Estante #${est.id_estante}
            </button>
          </div>
        `;
        fragmento.appendChild(ficha);
      }
      lista.replaceChildren(fragmento);
      atualizarSliders();
      requestAnimationFrame(atualizarSliders);
    } catch (erro) {
      resumo.textContent = 'Não foi possível carregar as estantes da API.';
      mostrarEstado(lista, 'Erro de conexão', 'Verifique se o servidor Python (python app.py --web) está rodando.');
    }
  }

  async function criarNovaEstante(evento) {
    evento.preventDefault();
    const form = evento.currentTarget;
    const fd = new FormData(form);
    const dominio_lado_1 = String(fd.get('dominio_lado_1') || '').trim();
    const dominio_lado_2 = String(fd.get('dominio_lado_2') || '').trim();
    const numero_de_livros = Number(fd.get('numero_de_livros') || 100);
    const resumo = document.getElementById('resumo-gerenciar-estantes');
    const botao = document.getElementById('botao-criar-estante');
    if (!dominio_lado_1 || !dominio_lado_2) {
      resumo.textContent = 'Preencha os temas dos dois lados da estante.';
      return;
    }
    botao.disabled = true;
    try {
      const base = API_BASE_URL.replace(/\/$/, '');
      const resp = await fetch(`${base}/estantes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ dominio_lado_1, dominio_lado_2, numero_de_livros })
      });
      const dados = await resp.json();
      if (!resp.ok) {
        resumo.textContent = dados.erro || 'Erro ao criar estante.';
        return;
      }
      form.reset();
      document.getElementById('estante-capacidade').value = '100';
      await carregarTelaGerenciarEstantes();
      resumo.textContent = `✅ Estante #${dados.id_estante} (${dominio_lado_1} / ${dominio_lado_2}) criada com sucesso!`;
    } catch (erro) {
      resumo.textContent = 'Erro ao comunicar com o servidor Python.';
    } finally {
      botao.disabled = false;
    }
  }

  async function confirmarExclusaoEstante(idEstante, tema, qtdLivros) {
    const aviso =
      `⚠️ ALERTA DE EXCLUSÃO EM CASCATA!\n\n` +
      `Você está prestes a apagar a Estante #${idEstante} (${tema}).\n` +
      `Isso vai apagar permanentemente TODOS os livros cadastrados nessa estante (${qtdLivros} livro(s) vinculado(s))!\n\n` +
      `Deseja realmente excluir esta estante e todos os livros dela?`;
    if (!window.confirm(aviso)) return;

    const resumo = document.getElementById('resumo-gerenciar-estantes');
    try {
      const base = API_BASE_URL.replace(/\/$/, '');
      const resp = await fetch(`${base}/estantes/${encodeURIComponent(idEstante)}`, {
        method: 'DELETE',
        headers: { Accept: 'application/json' }
      });
      const dados = await resp.json();
      if (!resp.ok) {
        resumo.textContent = dados.erro || 'Não foi possível excluir a estante.';
        return;
      }
      await carregarTelaGerenciarEstantes();
      resumo.textContent = `🗑️ Estante #${idEstante} excluída com sucesso (${dados.livros_removidos ?? 0} livro(s) removido(s) junto com ela).`;
    } catch (erro) {
      resumo.textContent = 'Erro ao tentar excluir a estante no servidor.';
    }
  }

  /* Ações do menu e da navegação entre telas. */
  const ACOES = {
    'abrir-avancadas': () => mostrarTela('avancada'),
    'voltar-avancadas': () => mostrarTela('avancada'),
    'voltar-joins': () => mostrarTela('joins'),
    'voltar-cadastro': () => mostrarTela(cadastroViaProcedure ? 'avancada' : 'principal'),
    'voltar-crud':     () => mostrarTela('principal'),
    'reabrir':         () => mostrarTela('principal'),
    'sair':            sairDoSistema,
    'listar-livros':   abrirListagem,
    'cadastrar-livro': () => abrirCadastro(false),
    'cadastrar-via-procedure': () => abrirCadastro(true),
    'gerenciar-estantes': carregarTelaGerenciarEstantes,
    'total-por-autor': () => mostrarTela('autor'),
    'consultas-join': () => mostrarTela('joins'),
    'estatisticas-genero': () => mostrarTela('relatorioGenero'),
    'busca-catalogo': () => mostrarTela('buscaCatalogo'),
    'estantes-vazias': consultarEstantesVazias,
    'acervo-critico': () => mostrarTela('acervoCritico'),
    'autores-unicos': consultarAutoresUnicos,
    'faixa-exemplares': () => mostrarTela('faixaExemplares'),
    'autores-multigenero': () => mostrarTela('autoresMultigenero'),
    'atualizar-livro': () => mostrarTela('atualizacao'),
    'excluir-livro':   () => mostrarTela('exclusao'),
    'sincronizar-pendencias': sincronizarPendencias,
  };

  document.addEventListener('click', (evento) => {
    const botaoExcluirEstante = evento.target.closest('[data-excluir-estante]');
    if (botaoExcluirEstante) {
      confirmarExclusaoEstante(
        botaoExcluirEstante.dataset.excluirEstante,
        botaoExcluirEstante.dataset.temaEstante,
        botaoExcluirEstante.dataset.qtdLivros
      );
      return;
    }
    const botao = evento.target.closest('[data-acao]');
    if (!botao) {
      const botaoJoin = evento.target.closest('[data-join]');
      if (botaoJoin) executarJoin(botaoJoin.dataset.join);
      return;
    }
    const acao = ACOES[botao.dataset.acao];
    if (acao) acao(botao);
  });

  document.getElementById('form-cadastro').addEventListener('submit', (e) => salvarFormulario(e, cadastroViaProcedure ? 'cadastro_procedure' : 'cadastro'));
  document.getElementById('form-criar-estante').addEventListener('submit', criarNovaEstante);
  document.getElementById('form-autor').addEventListener('submit', consultarAutor);
  document.getElementById('form-relatorio-genero').addEventListener('submit', consultarRelatorioGenero);
  document.getElementById('form-busca-catalogo').addEventListener('submit', buscarCatalogoPalavraChave);
  document.getElementById('form-acervo-critico').addEventListener('submit', consultarAcervoCritico);
  document.getElementById('form-faixa-exemplares').addEventListener('submit', buscarLivrosPorFaixa);
  document.getElementById('form-autores-multigenero').addEventListener('submit', consultarAutoresMultigenero);
  document.getElementById('form-atualizacao').addEventListener('submit', (e) => salvarFormulario(e, 'atualizacao'));
  document.getElementById('form-exclusao').addEventListener('submit', (e) => salvarFormulario(e, 'exclusao'));
  document.getElementById('exclusao-tipo').addEventListener('change', atualizarTipoExclusao);
  window.addEventListener('storage', atualizarAvisoPendencias);

  /* ------------------------------------------------------------------------
     4. SLIDER (barra de rolagem personalizada da tela de Ações Avançadas)
     ------------------------------------------------------------------------ */
  function iniciarSlider(lista, slider) {
    const trilho = slider.querySelector('.slider__trilho');
    const alca = slider.querySelector('.slider__alca');

    function atualizar() {
      const { scrollHeight, clientHeight, scrollTop } = lista;
      const rolavel = scrollHeight > clientHeight + 1;
      slider.classList.toggle('slider--inativo', !rolavel);
      if (!rolavel) {
        alca.style.height = '100%';
        alca.style.transform = 'translateY(0)';
        return;
      }
      const alturaTrilho = trilho.clientHeight;
      const alturaAlca = Math.max(alturaTrilho * 0.08, alturaTrilho * clientHeight / scrollHeight);
      const proporcao = scrollTop / (scrollHeight - clientHeight);
      alca.style.height = `${alturaAlca}px`;
      alca.style.transform = `translateY(${proporcao * (alturaTrilho - alturaAlca)}px)`;
    }

    lista.addEventListener('scroll', atualizar, { passive: true });
    window.addEventListener('resize', atualizar);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(atualizar);

    // arrastar a alça
    let arrasto = null;
    alca.addEventListener('pointerdown', (e) => {
      alca.setPointerCapture(e.pointerId);
      arrasto = { y: e.clientY, topo: lista.scrollTop };
      alca.classList.add('slider__alca--arrastando');
      e.preventDefault();
    });
    alca.addEventListener('pointermove', (e) => {
      if (!arrasto) return;
      const espaco = trilho.clientHeight - alca.offsetHeight;
      if (espaco <= 0) return;
      const fator = (lista.scrollHeight - lista.clientHeight) / espaco;
      lista.scrollTop = arrasto.topo + (e.clientY - arrasto.y) * fator;
    });
    const soltar = () => {
      arrasto = null;
      alca.classList.remove('slider__alca--arrastando');
    };
    alca.addEventListener('pointerup', soltar);
    alca.addEventListener('pointercancel', soltar);

    // clicar no trilho leva a alça até o ponto clicado
    trilho.addEventListener('pointerdown', (e) => {
      if (e.target === alca) return;
      const caixa = trilho.getBoundingClientRect();
      const espaco = caixa.height - alca.offsetHeight;
      if (espaco <= 0) return;
      const pos = Math.min(1, Math.max(0, (e.clientY - caixa.top - alca.offsetHeight / 2) / espaco));
      lista.scrollTo({ top: pos * (lista.scrollHeight - lista.clientHeight), behavior: 'smooth' });
    });

    // a roda do mouse sobre o slider também rola a lista
    slider.addEventListener('wheel', (e) => {
      lista.scrollBy({ top: e.deltaY });
      e.preventDefault();
    }, { passive: false });

    return atualizar;
  }

  /* ------------------------------------------------------------------------
     Início
     ------------------------------------------------------------------------ */
  const sliders = [
    iniciarSlider(document.getElementById('lista-avancada'), document.getElementById('slider-avancada')),
    iniciarSlider(document.getElementById('lista-livros'), document.getElementById('slider-livros')),
    iniciarSlider(document.getElementById('lista-autor'), document.getElementById('slider-autor')),
    iniciarSlider(document.getElementById('lista-join'), document.getElementById('slider-join')),
    iniciarSlider(document.getElementById('lista-relatorio-genero'), document.getElementById('slider-relatorio-genero')),
    iniciarSlider(document.getElementById('lista-busca-catalogo'), document.getElementById('slider-busca-catalogo')),
    iniciarSlider(document.getElementById('lista-estantes-vazias'), document.getElementById('slider-estantes-vazias')),
    iniciarSlider(document.getElementById('lista-acervo-critico'), document.getElementById('slider-acervo-critico')),
    iniciarSlider(document.getElementById('lista-autores-unicos'), document.getElementById('slider-autores-unicos')),
    iniciarSlider(document.getElementById('lista-faixa-exemplares'), document.getElementById('slider-faixa-exemplares')),
    iniciarSlider(document.getElementById('lista-autores-multigenero'), document.getElementById('slider-autores-multigenero')),
    iniciarSlider(document.getElementById('lista-gerenciar-estantes'), document.getElementById('slider-gerenciar-estantes'))
  ];
  atualizarSliders = () => sliders.forEach((atualizar) => atualizar());
  atualizarAvisoPendencias();
  atualizarTipoExclusao();
  iniciarCarrossel();
  telas.principal.querySelector('h1').focus({ preventScroll: true });
})();
