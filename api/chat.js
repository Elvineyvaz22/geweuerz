import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

let cachedCatalog = null;

function productSlug(value) {
  return value
    .toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

async function getProductCatalog() {
  if (cachedCatalog) return cachedCatalog;

  const file = await readFile(join(process.cwd(), 'products.json'), 'utf8');
  const products = JSON.parse(file);
  cachedCatalog = products
    .map((product) => {
      const link = `https://geweuerz.vercel.app/products/${productSlug(product.name)}.html`;
      return `- ${product.name} | ${product.category} | ${product.weight} | ${product.price} | ${link} | ${product.description}`;
    })
    .join('\n');

  return cachedCatalog;
}

async function getProducts() {
  const file = await readFile(join(process.cwd(), 'products.json'), 'utf8');
  return JSON.parse(file);
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, language = 'tr', currentProduct = null } = req.body || {};

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Message is required' });
    }

    if (!process.env.OPENAI_API_KEY) {
      return res.status(500).json({ error: 'OPENAI_API_KEY is not configured on Vercel.' });
    }

    const [productCatalog, products] = await Promise.all([getProductCatalog(), getProducts()]);
    const viewedProduct = currentProduct?.slug
      ? products.find((product) => productSlug(product.name) === currentProduct.slug)
      : null;
    const viewedProductContext = viewedProduct
      ? `The customer is currently viewing this product page: ${viewedProduct.name} | ${viewedProduct.category} | ${viewedProduct.weight} | ${viewedProduct.price} | ${viewedProduct.description}`
      : 'The customer is not currently on a specific product page.';

    const systemPrompt = `
You are the friendly AI sales assistant for Gewurz Kreationen Bonn, a spice and seasoning brand in Bonn, Germany.
Answer customers in Turkish if they write Turkish, German if they write German, Azerbaijani if they write Azerbaijani, otherwise answer in the detected language.
Keep answers short, warm, helpful, and sales-oriented.

Use only the product catalog below for product recommendations, prices, weights and categories.
Do not invent products, exact prices, stock levels, delivery dates, certificates, ingredients, or medical benefits.
If the customer asks for a recommendation, suggest 2-4 relevant products and briefly explain why.
If the customer wants to buy, order, ask about delivery, wholesale, partnership or exact stock, guide them to contact the business by email: info@gewuerzkreationen-bonn.de or visit the shop page: https://geweuerz.vercel.app/shop.html.
If asked about health or allergies, advise checking ingredients and contacting the business directly.

Current page context:
${viewedProductContext}

Product catalog:
${productCatalog}
`;

    const response = await fetch('https://api.openai.com/v1/responses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-5-mini',
        input: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: message },
        ],
        reasoning: { effort: 'minimal' },
        max_output_tokens: 700,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return res.status(response.status).json({ error: errorText });
    }

    const data = await response.json();
    const reply = data.output_text
      || data.output
        ?.flatMap((item) => item.content || [])
        ?.map((content) => content.text || '')
        ?.join('')
        ?.trim()
      || 'Uzgunum, su anda cevap veremedim.';

    return res.status(200).json({ reply });
  } catch (error) {
    return res.status(500).json({ error: error.message || 'Server error' });
  }
}
