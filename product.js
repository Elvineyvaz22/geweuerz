const productDetail = document.getElementById('productDetail');
const relatedProducts = document.getElementById('relatedProducts');

function productSlug(value) {
  return value
    .toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function orderLink(product) {
  const subject = encodeURIComponent(`Order request: ${product.name}`);
  const body = encodeURIComponent(`Hello,\n\nI would like to order or get more information about:\n${product.name} (${product.weight})\nPrice: ${product.price}\n\nThank you.`);
  return `mailto:info@gewuerzkreationen-bonn.de?subject=${subject}&body=${body}`;
}

function productCard(product) {
  const slug = productSlug(product.name);
  const article = document.createElement('article');
  article.className = 'shop-card';
  article.innerHTML = `
    <a class="shop-card-link" href="product.html?slug=${slug}" aria-label="${product.name}">
      <div class="shop-card-media">
        <span>${product.category}</span>
      </div>
      <div class="shop-card-body">
        <div class="shop-card-meta">
          <span>${product.weight}</span>
          <span>${product.unitPrice}</span>
        </div>
        <h2>${product.name}</h2>
        <p>${product.description}</p>
        <div class="shop-card-footer">
          <strong>${product.price}</strong>
          <span>Detay</span>
        </div>
      </div>
    </a>
  `;
  return article;
}

function renderProduct(product, products) {
  document.title = `${product.name} | Gewurz Kreationen Bonn`;
  productDetail.innerHTML = `
    <div class="product-detail-media">
      <span>${product.category}</span>
    </div>
    <div class="product-detail-content">
      <a class="product-back" href="shop.html">Magazaya qayit</a>
      <p class="eyebrow">${product.category}</p>
      <h1>${product.name}</h1>
      <p>${product.description}</p>
      <dl class="product-facts">
        <div><dt>Ceki</dt><dd>${product.weight}</dd></div>
        <div><dt>Qiymet</dt><dd>${product.price}</dd></div>
        <div><dt>100g qiymeti</dt><dd>${product.unitPrice}</dd></div>
      </dl>
      <div class="product-actions">
        <a class="btn primary" href="${orderLink(product)}">Siparis ucun yaz</a>
        <a class="btn secondary" href="shop.html">Butun mehsullar</a>
      </div>
    </div>
  `;

  const related = products
    .filter(item => item.category === product.category && item.name !== product.name)
    .slice(0, 3);

  relatedProducts.replaceChildren(...related.map(productCard));
}

async function initProductPage() {
  try {
    const response = await fetch('products.json');
    const products = await response.json();
    const slug = new URLSearchParams(window.location.search).get('slug');
    const product = products.find(item => productSlug(item.name) === slug);

    if (!product) {
      productDetail.innerHTML = `
        <div class="product-detail-content">
          <a class="product-back" href="shop.html">Magazaya qayit</a>
          <h1>Mehsul tapilmadi</h1>
          <p>Bu mehsul movcud kataloqda gorunmur.</p>
        </div>
      `;
      return;
    }

    renderProduct(product, products);
  } catch (error) {
    productDetail.innerHTML = '<p class="shop-empty">Mehsul melumati yuklene bilmedi.</p>';
  }
}

initProductPage();
