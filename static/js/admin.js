/* ==========================================================================
   KK_COLLECTIONS — Seller Admin Dashboard JavaScript
   Chart.js integrations, modal controls, inventory inline edits
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initModals();
});

function initModals() {
  // Add Product Modal
  const openAddBtn = document.getElementById('btn-open-add-product');
  const addModal = document.getElementById('modal-add-product');
  if (openAddBtn && addModal) {
    openAddBtn.addEventListener('click', () => {
      addModal.classList.add('active');
    });
  }

  // Edit Product Modal trigger
  document.querySelectorAll('.btn-edit-product').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = document.getElementById('modal-edit-product');
      if (!modal) return;

      const p = JSON.parse(btn.dataset.product);
      modal.querySelector('form').action = `/admin/products/edit/${p.product_id}`;
      modal.querySelector('[name="product_name"]').value = p.product_name;
      modal.querySelector('[name="category_id"]').value = p.category_id;
      modal.querySelector('[name="price"]').value = p.price;
      modal.querySelector('[name="discount"]').value = p.discount;
      modal.querySelector('[name="stock"]').value = p.stock;
      modal.querySelector('[name="material"]').value = p.material || '';
      modal.querySelector('[name="occasion"]').value = p.occasion || '';
      modal.querySelector('[name="description"]').value = p.description;

      modal.classList.add('active');
    });
  });

  // Edit Stock Modal trigger (in Inventory)
  document.querySelectorAll('.btn-edit-stock').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = document.getElementById('modal-edit-stock');
      if (!modal) return;

      modal.querySelector('[name="variant_id"]').value = btn.dataset.variantId;
      modal.querySelector('[name="stock"]').value = btn.dataset.currentStock;
      document.getElementById('stock-variant-title').textContent = btn.dataset.variantTitle;

      modal.classList.add('active');
    });
  });

  // Close modals on close button or backdrop click
  document.querySelectorAll('.close-modal-btn, .close-btn-cancel').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.admin-modal-backdrop').forEach(m => m.classList.remove('active'));
    });
  });

  document.querySelectorAll('.admin-modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('active');
      }
    });
  });
}
