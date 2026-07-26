# Pases de wallet — medición y receta para prenderlos

**Fecha de la medición: 2026-07-26.** Fase 3, puntos 2 y 3 del
`PLAN_CERO_REGRESIONES_2026-07-26.md`.

El código de los dos proveedores **ya está escrito, conectado y probado**
(`books/scripts/wallet_passes.py`, `books/scripts/test_wallet_passes.py`), y los
dos están **apagados**. Prender cualquiera de los dos es poner credenciales y
cambiar una repo var a `true`. No hay que volver a tocar código.

---

## Lo que cuesta cada uno (medido, no estimado)

| | Google Wallet | Apple Wallet |
|---|---|---|
| Dinero | **$0** | **$99 USD/año** (Apple Developer Program) |
| Cuenta de servicio de Google Cloud | **Sí**, y firma del lado del servidor | No |
| Verificación de identidad | **Sí**: Business Profile + perfil de pagos | Sí, la del programa de Apple |
| Revisión manual del proveedor | **Sí**, sin plazo publicado | La del alta del certificado |
| ¿Funciona antes de la aprobación? | **No para huéspedes reales** | Sí, en cuanto hay certificado |

### Por qué Google Wallet NO se prendió el 2026-07-26

La API no cobra, pero eso no quiere decir que sea barata. La medición contra la
documentación oficial:

1. **El botón se arma con un JWT firmado.** El link es
   `https://pay.google.com/gp/v/save/<JWT>`, firmado con la llave de una cuenta
   de servicio de Google Cloud. **No se puede firmar en el navegador**, así que
   la guía —que es HTML estático en GitHub Pages— no puede armarlo sola. Aquí se
   firma en el generador, con la llave como secret del repo.
   [Doc](https://developers.google.com/wallet/generic/web)
2. **Hay que darse de alta como Issuer** en la Google Pay & Wallet Console, con
   nombre público del negocio y aceptación de términos.
3. **Para publicar hay que completar el Business Profile y dar de alta un perfil
   de pagos que verifica la identidad**, además de tener al menos una Passes
   Class.
   [Doc](https://developers.google.com/wallet/generic/test-and-go-live/request-publishing-access)
4. **Google revisa a mano** y avisa cuando aprueba. No publican plazo.
5. **Hasta que aprueban, la cuenta está en demo mode**: el pase sale marcado
   `[TEST ONLY]` y **solo lo pueden guardar las cuentas con rol Admin o
   Developer y las cuentas de prueba dadas de alta**. Un huésped real toca el
   botón y no le pasa nada.

El punto 5 es el que decidió. Publicar hoy ese botón sería poner en la guía de
un cliente que ya pagó un botón que **no funciona para nadie que no esté en la
lista de pruebas de Vero**, y no falla con error: no hace nada. Es exactamente
la clase de fallo silencioso por la que existe el PLAN CERO REGRESIONES. Por eso
se paró, se dejó escrito y probado, y se prende el día que Google apruebe.

---

## Prender Google Wallet

1. **Alta de Issuer** en <https://pay.google.com/business/console> → Google
   Wallet API. Anota el **Issuer ID** (un número largo).
2. **Cuenta de servicio** en Google Cloud, con la Google Wallet API habilitada.
   Descarga su JSON. En la consola de Wallet, dale acceso a esa cuenta de
   servicio sobre el Issuer.
3. **Business Profile + perfil de pagos** y **Request publishing access**.
   Espera la aprobación de Google.
4. En GitHub → Settings → Secrets and variables → Actions:
   - Secret `GOOGLE_WALLET_SERVICE_ACCOUNT_JSON` = el JSON completo, tal cual.
   - Variable `GOOGLE_WALLET_ISSUER_ID` = el Issuer ID.
   - Variable `MYGUEST_GOOGLE_WALLET_ENABLED` = `true`.
5. Regenera una guía y ábrela en un Android. El botón aparece solo si el JWT
   quedó bien firmado y mide menos de 1800 caracteres (el generador avisa en el
   log si se pasa, y en ese caso deja la guía sin botón en vez de publicar un
   link que el navegador trunca).

> **Antes de salir a producción:** Google pide usar su botón de marca oficial.
> Hoy el botón usa el estilo de la guía. Cámbialo por el asset oficial de
> <https://developers.google.com/wallet/generic/resources/brand-guidelines> en
> `books/templates/master.html`, en el bloque `#google-wallet-btn`.

---

## Prender Apple Wallet

1. Paga el **Apple Developer Program** ($99 USD/año).
2. En el portal, crea un **Pass Type ID** (por ejemplo
   `pass.com.myguestguide.stay`) y genera su certificado. Anota tu **Team ID**.
3. Convierte el certificado a PEM y saca también el **intermedio WWDR** de
   Apple:

   ```bash
   openssl pkcs12 -in Certificates.p12 -clcerts -nokeys -out pass-cert.pem
   openssl pkcs12 -in Certificates.p12 -nocerts -nodes -out pass-key.pem
   openssl x509 -inform DER -in AppleWWDRCAG4.cer -out wwdr.pem
   ```

4. En GitHub → Settings → Secrets and variables → Actions:
   - Secrets `APPLE_WALLET_CERT_PEM`, `APPLE_WALLET_KEY_PEM`,
     `APPLE_WALLET_WWDR_PEM` (y `APPLE_WALLET_KEY_PASSWORD` solo si la llave
     tiene contraseña).
   - Variables `APPLE_WALLET_PASS_TYPE_ID`, `APPLE_WALLET_TEAM_ID` y
     `MYGUEST_APPLE_WALLET_ENABLED` = `true`.
5. **Verifica el content-type antes de dar por bueno el botón.** El `.pkpass`
   se publica junto a la guía; iOS solo lo abre en Wallet si el servidor lo
   manda con su tipo correcto:

   ```bash
   curl -sI https://myguestguide.com/villas/<slug>/pass.pkpass | grep -i content-type
   ```

   Tiene que decir `application/vnd.apple.pkpass`. Si dice
   `application/octet-stream`, el pase se descarga como archivo suelto y Wallet
   no lo abre. Se arregla con una Transform Rule de Cloudflare que fije el
   header para `/villas/*/pass.pkpass`, sin tocar nada del repo.
6. Abre la guía en un iPhone y guarda el pase.

> **Los certificados de Apple caducan al año.** Si caduca, la generación **no**
> se cae: el generador avisa en el log (`[wallet] AVISO:`) y la guía sale sin
> botón. Eso es a propósito — la guía es el producto, el botón es un extra, y un
> certificado vencido no puede tumbar la entrega de un cliente que ya pagó.

---

## Lo que va dentro de un pase (y lo que nunca)

Un pase se comparte igual que una tarjeta de contacto, así que lleva **solo lo
que ya es público** en el sitio:

- nombre de la propiedad
- dirección
- link a `https://myguestguide.com/villas/<slug>/` — **sin token**

Nunca: WiFi, códigos, lockbox, teléfono del anfitrión, ni el link `?token=`.

El link sin token abre el mismo shell público que ya está en GitHub Pages: el
huésped que vuelve encuentra la propiedad, su dirección, el mapa y las
recomendaciones, y no se filtra nada. El link con token abre WiFi y códigos, y
por eso no viaja en el pase — la misma decisión que se tomó con el `.vcf`.

Esto no es una promesa: `books/scripts/test_wallet_passes.py` abre el pase
generado y falla si aparece cualquiera de esos marcadores dentro.
