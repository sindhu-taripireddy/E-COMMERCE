/* ==========================================================================
   KK_COLLECTIONS — Main Storefront JavaScript
   Cart drawer/management, wishlist toggle, notifications, coupons
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initToasts();
  initWishlistButtons();
  initAddToCartButtons();
  initCheckoutPaymentTabs();
  initCouponCode();
  initReviewForm();
});

// Toast Notification Utility
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 360px;
    `;
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  const bg = type === 'success' ? '#198754' : (type === 'danger' ? '#DC3545' : '#5B1426');
  toast.style.cssText = `
    background: ${bg};
    color: #FFFFFF;
    padding: 12px 18px;
    border-radius: 8px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.2);
    font-size: 0.88rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    animation: slideIn 0.3s ease forwards;
    border-left: 4px solid #C5A059;
  `;
  toast.innerHTML = `
    <span>${message}</span>
    <button style="background:none;border:none;color:#FFF;cursor:pointer;font-size:1.1rem;">&times;</button>
  `;

  toast.querySelector('button').onclick = () => toast.remove();
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

function initToasts() {
  // Flash messages auto-dismiss
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(a => {
    setTimeout(() => {
      a.style.opacity = '0';
      a.style.transition = 'opacity 0.5s ease';
      setTimeout(() => a.remove(), 500);
    }, 4500);
  });
}

// Wishlist Toggle
function initWishlistButtons() {
  document.querySelectorAll('.wishlist-heart-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const productId = btn.dataset.productId;
      if (!productId) return;

      try {
        const res = await fetch('/api/wishlist/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: productId })
        });
        const data = await res.json();
        if (data.success) {
          if (data.is_in_wishlist) {
            btn.classList.add('active');
            btn.querySelector('i')?.classList.replace('far', 'fas');
          } else {
            btn.classList.remove('active');
            btn.querySelector('i')?.classList.replace('fas', 'far');
          }
          // Update header counter
          const counter = document.getElementById('header-wishlist-count');
          if (counter) counter.textContent = data.total_count;
          showToast(data.message, 'success');
        }
      } catch (err) {
        console.error('Wishlist error:', err);
      }
    });
  });
}

// Add to Cart
function initAddToCartButtons() {
  document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const productId = btn.dataset.productId;
      const variantId = btn.dataset.variantId || null;
      const qtyInput = document.getElementById('product-quantity-input');
      const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

      if (!productId) return;

      btn.disabled = true;
      const origText = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';

      try {
        const res = await fetch('/api/cart/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: productId, variant_id: variantId, quantity: quantity })
        });
        const data = await res.json();
        if (data.success) {
          // Update header badges
          const countBadge = document.getElementById('header-cart-count');
          if (countBadge) countBadge.textContent = data.cart.total_items;
          showToast(data.message, 'success');
        } else {
          showToast(data.error || 'Failed to add item', 'danger');
        }
      } catch (err) {
        console.error('Add to cart error:', err);
        showToast('Could not add to cart. Please try again.', 'danger');
      } finally {
        btn.disabled = false;
        btn.innerHTML = origText;
      }
    });
  });
}

// Cart Quantity Adjustments (On Cart Page)
window.updateCartQuantity = async function(itemId, newQty) {
  if (newQty < 1) return;
  try {
    const res = await fetch('/api/cart/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId, quantity: newQty })
    });
    const data = await res.json();
    if (data.success) {
      location.reload();
    }
  } catch (err) {
    console.error(err);
  }
};

window.removeCartItem = async function(itemId) {
  if (!confirm('Remove this lovely piece from your bag?')) return;
  try {
    const res = await fetch('/api/cart/remove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId })
    });
    const data = await res.json();
    if (data.success) {
      location.reload();
    }
  } catch (err) {
    console.error(err);
  }
};

// Checkout Payment Tabs
function initCheckoutPaymentTabs() {
  const methodRadios = document.querySelectorAll('input[name="payment_method"]');
  const upiBox = document.getElementById('upi-payment-details');
  const cardBox = document.getElementById('card-payment-details');
  const netBankingBox = document.getElementById('netbanking-payment-details');
  const codBox = document.getElementById('cod-payment-details');

  if (!methodRadios.length) return;

  function updatePaymentView(val) {
    if (upiBox) upiBox.style.display = (val === 'UPI') ? 'block' : 'none';
    if (cardBox) cardBox.style.display = (val === 'Card') ? 'block' : 'none';
    if (netBankingBox) netBankingBox.style.display = (val === 'Net Banking') ? 'block' : 'none';
    if (codBox) codBox.style.display = (val === 'COD') ? 'block' : 'none';
  }

  methodRadios.forEach(radio => {
    radio.addEventListener('change', (e) => updatePaymentView(e.target.value));
  });

  const checked = document.querySelector('input[name="payment_method"]:checked');
  if (checked) updatePaymentView(checked.value);
}

// Coupon Code Validation
function initCouponCode() {
  const applyBtn = document.getElementById('apply-coupon-btn');
  const input = document.getElementById('coupon-code-input');
  if (!applyBtn || !input) return;

  applyBtn.addEventListener('click', async () => {
    const code = input.value.trim();
    const subtotalEl = document.getElementById('cart-subtotal-val');
    const subtotal = subtotalEl ? parseFloat(subtotalEl.dataset.subtotal) : 0;

    if (!code) {
      showToast('Please enter a coupon code', 'warning');
      return;
    }

    try {
      const res = await fetch('/api/coupon/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, subtotal: subtotal })
      });
      const data = await res.json();
      if (data.success) {
        showToast(data.message, 'success');
        const discRow = document.getElementById('discount-row');
        const discVal = document.getElementById('discount-amount-val');
        const totalVal = document.getElementById('cart-total-val');
        const hiddenInput = document.getElementById('checkout-discount-code');

        if (discRow) discRow.style.display = 'flex';
        if (discVal) discVal.textContent = `-₹${data.discount}`;
        if (totalVal) totalVal.textContent = `₹${data.new_total}`;
        if (hiddenInput) hiddenInput.value = code;
      } else {
        showToast(data.message, 'danger');
      }
    } catch (err) {
      showToast('Error validating coupon', 'danger');
    }
  });
}

// Review Submission
function initReviewForm() {
  const form = document.getElementById('product-review-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const productId = form.dataset.productId;
    const name = form.querySelector('[name="customer_name"]')?.value || 'Valued Customer';
    const rating = form.querySelector('[name="rating"]:checked')?.value || 5;
    const comment = form.querySelector('[name="comment"]')?.value;

    if (!comment) {
      showToast('Please enter your review feedback', 'warning');
      return;
    }

    try {
      const res = await fetch('/api/reviews/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, customer_name: name, rating: rating, comment: comment })
      });
      const data = await res.json();
      if (data.success) {
        showToast(data.message, 'success');
        setTimeout(() => location.reload(), 1000);
      }
    } catch (err) {
      showToast('Could not submit review', 'danger');
    }
  });
}
