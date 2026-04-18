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

## Modo seguro de UI

Se a aplicação abrir mas o layout estiver quebrado, use:

- `?safe_mode=1` na URL, ou
- variável de ambiente `SAFE_MODE=1`

Isso desativa CSS customizado para facilitar diagnóstico de renderização.
