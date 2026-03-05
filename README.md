# 316 - Meta Ads API Integration

Integração com a API de Anúncios da Meta (Facebook Ads) para consultar contas, campanhas e métricas de performance.

## Pré-requisitos

- Python 3.8+
- Conta no [Meta for Developers](https://developers.facebook.com/)
- App configurado com permissões de Ads Management

## Configuração

### 1. Criar o App no Meta for Developers

1. Acesse [developers.facebook.com/apps](https://developers.facebook.com/apps/)
2. Clique em **Criar App** → selecione **Negócios**
3. Anote o **App ID** e o **App Secret** (em Configurações → Básico)

### 2. Gerar o Access Token

1. Acesse o [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Selecione seu App
3. Clique em **Gerar Token de Acesso**
4. Adicione as permissões necessárias:
   - `ads_management`
   - `ads_read`
   - `read_insights`
5. Para uso em produção, converta para **Long-Lived Token** (validade de 60 dias) ou use um **System User Token** (sem expiração)

### 3. Configurar as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
FB_APP_ID=seu_app_id
FB_APP_SECRET=seu_app_secret
FB_ACCESS_TOKEN=seu_access_token
```

### 4. Instalar as dependências

```bash
pip install -r requirements.txt
```

## Uso

### Verificar conexão e listar contas

```bash
python ads_api.py
```

Exibe as contas de anúncio vinculadas ao token, suas campanhas e insights dos últimos 7 dias.

### Analisar campanhas (últimos 30 dias)

```bash
python analyze_campaigns.py
```

Mostra um relatório detalhado por campanha com:
- Gasto, alcance, impressões, cliques
- CTR, CPC, CPM, frequência
- Leads, compras e custos por ação (CPL, CPP)
- Rankings de melhor/pior performance

## Estrutura do projeto

```
.
├── ads_api.py           # Funções de conexão e consulta à API
├── analyze_campaigns.py # Análise detalhada de campanhas
├── requirements.txt     # Dependências Python
├── .env.example         # Modelo de variáveis de ambiente
└── .env                 # Suas credenciais (não versionado)
```

## Permissões necessárias no Meta App

| Permissão | Finalidade |
|-----------|-----------|
| `ads_management` | Gerenciar anúncios e campanhas |
| `ads_read` | Ler dados de anúncios |
| `read_insights` | Acessar métricas de performance |

## Referências

- [Meta Marketing API - Documentação](https://developers.facebook.com/docs/marketing-api/)
- [Facebook Business SDK para Python](https://github.com/facebook/facebook-python-business-sdk)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
