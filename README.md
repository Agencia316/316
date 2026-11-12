# 316

- `dashboard.py` — dashboard Meta Ads (`streamlit run dashboard.py`)
- `painel_juridico.py` — painel da API do Robô Jurídico para embutir no CRM Umbra (`streamlit run painel_juridico.py`)

## Painel jurídico no Umbra
1. Suba a API (`consulta-processos api`) em servidor/IP brasileiro e crie um cliente/chave em `/admin`.
2. Configure `JURIDICO_API_URL` e `JURIDICO_API_KEY` (secrets do Streamlit ou `.env`). A chave fica só no servidor do painel.
3. No Umbra, embuta: `<iframe src="https://SEU-PAINEL/?embed=true&oab_uf=MG&oab_numero=123456&processo=NUMERO_CNJ"></iframe>`
   (parâmetros opcionais: `processo`, `oab_uf`, `oab_numero`, `dias`).
