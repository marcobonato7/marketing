# Renn Shopify theme (v3.8)

Online Store 2.0 theme for Renn. The page opens with the neck cream's pour, which plays by itself and lands on the gua sha tube. Scrolling then plays each mask's own pour and lands on its product card, ending on the bundle. The animation is a 362-frame sequence in `assets/seq-*.jpg` that ships inside the theme, so there is nothing to upload, and it works on phones. The page also has a shop grid, product pages, a routine picker, ingredients, reviews, FAQ and an email signup.

| Stop | Product | Pour colour |
|---|---|---|
| 01 | PDRN Collagen Gua Sha Neck Wrinkle Cream ($35) | pink cream |
| 02 | Zero Pore Blackhead Mud Mask ($25) | blue |
| 03 | Collagen Night Wrapping Mask ($25) | clear |
| 04 | PDRN Pink Caffeine Night Wrapping Mask ($25) | pink shimmer |
| 05 | Kojic Acid Turmeric Night Wrapping Mask ($25) | gold |
| 06 | The Full Routine bundle ($75) | |

Each product is matched to its colour by its name, so the order of the film blocks doesn't matter.

## Connect to Shopify
1. In Shopify admin, go to **Online Store > Themes > Add theme > Connect from GitHub**.
2. Pick the `marketing` repo and the `renn-shopify-theme` branch.
3. **Publish** that theme. It must be the current theme for visitors to see it.
4. Create the products in Shopify, then pick them in the five "Product pour" blocks. Pick the bundle in **Theme settings > Bundle**.

## Check which version is live
Add `?renn-debug` to your store's address. The bar at the bottom should say **film 3.8**.

## Edit
- Prices, photos, product names: in **Products** (the theme reads them from Shopify).
- Text: in **Customize**, click any section.
- Social links and contact email: **Theme settings > Renn**.
