# Troubleshooting de acesso

## Erro `NET::ERR_CERT_AUTHORITY_INVALID` com HSTS

Se o navegador mostrar mensagens como:

- "Sua conexão não é particular"
- `net::ERR_CERT_AUTHORITY_INVALID`
- "Você não pode visitar ... porque o site usa HSTS"

isso normalmente **não é um erro de CSS ou do código da aplicação**. Em geral indica:

- inspeção HTTPS por antivírus/firewall corporativo;
- proxy/rede Wi‑Fi com interceptação TLS;
- certificado raiz ausente/desatualizado no dispositivo.

### Como validar rapidamente

1. Abra o mesmo link em outra rede (ex.: 4G/5G do celular).
2. Teste em outro dispositivo/navegador.
3. Verifique data/hora do sistema.
4. Desative temporariamente inspeção HTTPS do antivírus/proxy (se permitido).
5. Em ambiente corporativo, peça ao TI para instalar a cadeia de certificados correta.
6. Como contingência, rode localmente: `streamlit run app.py`.

## Modo seguro de UI

Se a aplicação abrir mas o layout estiver quebrado, use:

- `?safe_mode=1` na URL, ou
- variável de ambiente `SAFE_MODE=1`

Isso desativa CSS customizado para facilitar diagnóstico de renderização.

## Configurar chave via `st.secrets`

Para deploy no Streamlit Cloud, prefira configurar a API key em **Secrets**:

```toml
GEMINI_API_KEY="sua_chave_aqui"
```

O app agora prioriza `st.secrets` e usa variáveis de ambiente apenas como fallback.

### Passo a passo (Streamlit Cloud)

1. Abra o app no painel do Streamlit Cloud.
2. Vá em **Settings > Secrets**.
3. Cole:

```toml
GEMINI_API_KEY="sua_chave_aqui"
```

4. Salve e reinicie o app.

### Passo a passo (rodando local)

1. Crie o arquivo `.streamlit/secrets.toml` na raiz do projeto.
2. Adicione:

```toml
GEMINI_API_KEY="sua_chave_aqui"
```

3. Rode `streamlit run app.py`.

### Como ler no código

No código Python:

```python
api_key = st.secrets.get("GEMINI_API_KEY")
```

Neste projeto, a leitura já está implementada com fallback para variáveis de ambiente.
