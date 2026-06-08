const shopGrid = document.getElementById('shopGrid');
const shopCategories = document.getElementById('shopCategories');
const shopSearch = document.getElementById('shopSearch');
const shopSort = document.getElementById('shopSort');
const shopCount = document.getElementById('shopCount');

let products = [];
let activeCategory = 'all';

function normalizeText(value) {
  return value.toLowerCase().trim();
}

function productSlug(value) {
  return value
    .toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function productPageUrl(product) {
  return `products/${productSlug(product.name)}.html`;
}

function createCategoryButton(category) {
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = category === 'all' ? 'Tumu' : category;
  button.className = category === activeCategory ? 'active' : '';
  button.addEventListener('click', () => {
    activeCategory = category;
    renderShop();
  });
  return button;
}

function renderCategories() {
  const categories = ['all', ...new Set(products.map(product => product.category))];
  shopCategories.replaceChildren(...categories.map(createCategoryButton));
}

function getFilteredProducts() {
  const query = normalizeText(shopSearch.value || '');
  let result = products.filter((product) => {
    const matchesCategory = activeCategory === 'all' || product.category === activeCategory;
    const searchable = normalizeText(`${product.name} ${product.category} ${product.description}`);
    return matchesCategory && (!query || searchable.includes(query));
  });

  if (shopSort.value === 'name') {
    result = result.sort((a, b) => a.name.localeCompare(b.name));
  }

  if (shopSort.value === 'category') {
    result = result.sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));
  }

  return result;
}

function renderProduct(product) {
  const article = document.createElement('article');
  article.className = 'shop-card';
  article.innerHTML = `
    <a class="shop-card-link" href="${productPageUrl(product)}" aria-label="${product.name}">
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

function renderShop() {
  renderCategories();
  const filteredProducts = getFilteredProducts();
  shopCount.textContent = `${filteredProducts.length} Produkte`;
  shopGrid.replaceChildren(...filteredProducts.map(renderProduct));
}

async function initShop() {
  try {
    const response = await fetch('products.json');
    products = await response.json();
    renderShop();
  } catch (error) {
    shopGrid.innerHTML = '<p class="shop-empty">Produkte konnten nicht geladen werden.</p>';
  }
}

shopSearch?.addEventListener('input', renderShop);
shopSort?.addEventListener('change', renderShop);

initShop();
