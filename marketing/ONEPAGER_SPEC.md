# One-pager de ventas de My Guest — especificación para reconstruirlo

> Escrito 2026-07-25 en la sesión guiada de pendientes de Vero.
> **Por qué existe este archivo:** el `MyGuest_Sales_OnePager.pdf` actual lo generó una
> sesión previa de Claude **sin dejar el HTML fuente** en el repo (solo quedó el PDF).
> Verificado: no hay ningún archivo en `C:\Users\veron` con el copy del one-pager.
> Así que no se puede "editar": hay que reconstruirlo. Aquí queda todo lo necesario.

## Estado

- Archivo actual: `marketing/assets/MyGuest_Sales_OnePager.pdf` (1 página, Letter vertical).
- 🔴 **Dice `$29 launch price`. El precio real es `$49 USD`** (verificado contra
  `public/index.html:372` — `$129` tachado, `$49` vigente; y contra el Centro de Control).
- **No mandarlo a ningún prospecto hasta regenerarlo.**

## Los 6 cambios que pidió Vero (2026-07-25)

1. **Precio: `$29` → `$49`.**
2. **El mockup del celular no parece un celular.** Es beige y el fondo blanco detrás lo
   aplana. Debe verse como un celular realista.
3. **El QR está descuadrado** dentro de la tarjeta teal de abajo a la derecha.
4. **"Local restaurants & recommendations" se sale del recuadro blanco** de la sección
   "What your guests receive" (desbordamiento de texto).
5. **"How it works", paso 1:** hoy dice *"Send your PDF, Canva, photos or notes."* — debe
   explicar que **el cliente llena un formulario** en el que puede anexar su PDF o sus notas.
6. **Más espacio arriba** de la fila del botón "Get my welcome book" + la pastilla del precio.

## Assets que ya existen (no hay que crear nada)

| Qué | Ruta |
|---|---|
| ✅ **Celular realista (resuelve el punto 2)** | `marketing/instagram/assets/mockups/phone/coastal-phone.png` — iPhone con marco **negro** y la guía de The Palm House ya dentro. Es el que la sesión previa NO usó. Variantes: `classic-phone.png`, `minimalist-phone.png`, `sunset-phone.png` |
| Logo | `public/landing/logo_principal-Photoroom.png` |
| Mascota | `public/landing/mascota-photoroom.png` |
| Screenshots de los 4 demos | `marketing/pinterest/assets/screenshots/<slug>/` |

## Paleta de marca (de `CLAUDE.md`)

`#F7F3EE` Warm Ivory · `#EFE7DD` Soft Sand · `#2B2B2B` Soft Charcoal · `#7A746E` Warm Gray
`#D8CEC2` Light Taupe · `#59C3C3` Lagoon Teal · `#2D6A73` Deep Teal · `#F29B7F` Sunset Coral

## Cómo renderizarlo

Playwright ya está instalado en esta máquina (`python -c "import playwright"` → OK).
Construir `marketing/onepager/onepager.html` (Letter, 816×1056 px @96dpi) y renderizar a PDF.
**Guardar el HTML fuente en el repo** para que el próximo cambio de precio sea de un minuto.

## Regla que este incidente deja

El precio vive en `public/index.html` y en Stripe. Cualquier material de venta que
lo repita (PDF, pines, posts) es una copia que se desincroniza sola. Al cambiar un
precio hay que barrer los materiales, no solo la landing.

## Pendiente hermano del mismo defecto

`marketing/instagram/posts.json` tiene **4 posts con `"price": "29"`** en el campo que
se imprime en la imagen, mientras su propio `caption` ya dice `$49` — el post se
contradice a sí mismo. Son `post-024`, `post-025` y otros dos (líneas ~353, 369, 404, 420).
Están en `status: "draft"`, así que no se han publicado. **Corregirlos en la misma sesión.**
