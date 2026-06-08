export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, language = 'tr' } = req.body || {};

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Message is required' });
    }

    if (!process.env.OPENAI_API_KEY) {
      return res.status(500).json({ error: 'OPENAI_API_KEY is not configured on Vercel.' });
    }

    const systemPrompt = `
You are the friendly AI assistant for Gewürz Kreationen Bonn, a spice and seasoning brand in Bonn, Germany.
Answer customers in Turkish if they write Turkish, in German if they write German, otherwise answer in the detected language.
Keep answers short, warm, helpful, and sales-oriented.
You can help with:
- spice recommendations for meat, chicken, fish, vegetables, soups, salads and Turkish/German dishes
- product guidance
- gift set suggestions
- general order/contact guidance
If the customer wants to buy, order, ask about price, delivery, wholesale, partnership or exact stock, guide them to contact the business by email: info@gewuerzkreationen-bonn.de.
Do not invent exact prices, stock levels, delivery dates, certificates, ingredients, or medical benefits.
If asked about health or allergies, advise checking ingredients and contacting the business directly.
`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: message }
        ],
        temperature: 0.5,
        max_tokens: 350,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return res.status(response.status).json({ error: errorText });
    }

    const data = await response.json();
    const reply = data.choices?.[0]?.message?.content || 'Üzgünüm, şu anda cevap veremedim.';

    return res.status(200).json({ reply });
  } catch (error) {
    return res.status(500).json({ error: error.message || 'Server error' });
  }
}
