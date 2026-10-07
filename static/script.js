/* ImpactEcho Dashboard — fully dynamic from backend */

// Retrieve saved wallet address (with fallback to blockchainUser)
let walletAddress = localStorage.getItem('walletAddress') || "";

// If walletAddress is not set but blockchainUser exists, use that
if (!walletAddress) {
  const blockchainUser = localStorage.getItem('blockchainUser');
  if (blockchainUser) {
    try {
      const userData = JSON.parse(blockchainUser);
      walletAddress = userData.address || "";
      // Store it for future use
      if (walletAddress) {
        localStorage.setItem('walletAddress', walletAddress);
      }
    } catch (e) {
      console.error('Error parsing blockchainUser:', e);
    }
  }
}

// Get user profile (name/email) if available
function getUserProfile(walletAddress) {
  const profileKey = `userProfile_${walletAddress}`;
  const profile = localStorage.getItem(profileKey);
  return profile ? JSON.parse(profile) : null;
}

const userProfile = getUserProfile(walletAddress);

// Use profile name if available, otherwise wallet address
// Make user global so chatbot can access it
window.user = { 
  username: userProfile && userProfile.name ? userProfile.name : (walletAddress ? `${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}` : "Guest"),
  walletAddress: walletAddress,
  email: userProfile ? userProfile.email : ""
};
const user = window.user;
const livesPer25 = 25;

/* --- DOM References --- */
const usernameBanner = document.getElementById("username-banner");
const welcomeInline = document.getElementById("welcomeInline");
const usernameInput = document.getElementById("usernameInput");
const causesGrid = document.getElementById("causesGrid");
const totalImpactEl = document.getElementById("totalImpact");
const donationsMadeEl = document.getElementById("donationsMade");
const causesSupportedEl = document.getElementById("causesSupported");
const livesImpactedEl = document.getElementById("livesImpacted");
const impactProgressBar = document.getElementById("impactProgressBar");
const impactPercent = document.getElementById("impactPercent");
const recentList = document.getElementById("recentList");

/* --- State --- */
let causes = [];
// Make these global so chatbot can access them
window.totalImpact = 0;
window.donationsMade = 0;
window.livesImpacted = 0;
window.supportedCauses = new Set();
window.recentDonations = [];
let selectedCause = null; // For confirmation modal

// Convenience accessors
const getTotalImpact = () => window.totalImpact;
const getDonationsMade = () => window.donationsMade;
const getLivesImpacted = () => window.livesImpacted;
const getSupportedCauses = () => window.supportedCauses;
const getRecentDonations = () => window.recentDonations;

/* --- User Data Persistence Functions --- */
function getUserDataKey() {
  return `userData_${user.walletAddress}`;
}

function saveUserData() {
  if (!user.walletAddress) return;
  
  const userData = {
    totalImpact: window.totalImpact,
    donationsMade: window.donationsMade,
    livesImpacted: window.livesImpacted,
    supportedCauses: Array.from(window.supportedCauses),
    recentDonations: window.recentDonations,
    lastUpdated: new Date().toISOString()
  };
  
  localStorage.setItem(getUserDataKey(), JSON.stringify(userData));
}

function loadUserData() {
  if (!user.walletAddress) return;
  
  const savedData = localStorage.getItem(getUserDataKey());
  if (savedData) {
    try {
      const userData = JSON.parse(savedData);
      // Update global window variables for chatbot access
      window.totalImpact = userData.totalImpact || 0;
      window.donationsMade = userData.donationsMade || 0;
      window.livesImpacted = userData.livesImpacted || 0;
      
      // Restore supportedCauses Set
      if (userData.supportedCauses) {
        window.supportedCauses.clear();
        userData.supportedCauses.forEach(id => window.supportedCauses.add(id));
      }
      
      // Restore recentDonations array
      if (userData.recentDonations) {
        window.recentDonations.length = 0;
        window.recentDonations.push(...userData.recentDonations);
      }
      
      // Update UI with loaded data
      updateStats();
      renderRecentDonations();
    } catch (err) {
      console.error('Error loading user data:', err);
    }
  }
}

/* --- Helper Functions --- */
const formatINR = (num) => "₹" + Number(num).toLocaleString();

/* --- Username Logic --- */
function renderUsername() {
  usernameBanner.textContent = user.username;
  welcomeInline.textContent = user.username;
  
  // Show user's name or wallet address in the input field
  if (userProfile && userProfile.name) {
    usernameInput.value = userProfile.name;
  } else {
    usernameInput.value = user.walletAddress || "Not Connected";
  }
  
  usernameInput.readOnly = true;
  usernameInput.style.cursor = "not-allowed";
  usernameInput.style.opacity = "0.7";
  usernameInput.placeholder = "Click to edit profile";
  
  // Add click handler to edit profile
  usernameInput.onclick = () => {
    showEditProfileModal();
  };
  usernameInput.style.cursor = "pointer";
  
  // Render badge after username
  renderBadge();
}

/* --- Badge System --- */
const BADGE_RANKS = [
  { name: 'Bronze Guardian', icon: '🥉', threshold: 10000, class: 'badge-bronze', color: '#CD7F32' },
  { name: 'Silver Benefactor', icon: '🥈', threshold: 50000, class: 'badge-silver', color: '#C0C0C0' },
  { name: 'Gold Philanthropist', icon: '🥇', threshold: 150000, class: 'badge-gold', color: '#FFD700' },
  { name: 'Platinum Champion', icon: '💎', threshold: 500000, class: 'badge-platinum', color: '#E5E4E2' },
  { name: 'Diamond Legend', icon: '👑', threshold: 1000000, class: 'badge-diamond', color: '#00d4ff' }
];

function getBadgeRank(totalDonations) {
  for (let i = BADGE_RANKS.length - 1; i >= 0; i--) {
    if (totalDonations >= BADGE_RANKS[i].threshold) {
      return BADGE_RANKS[i];
    }
  }
  return null; // No badge yet
}

function renderBadge() {
  const badgeContainer = document.getElementById('userBadge');
  if (!badgeContainer) return;
  
  const totalDonations = window.totalImpact || 0;
  const currentBadge = getBadgeRank(totalDonations);
  
  if (currentBadge) {
    // Render current badge with info button
    badgeContainer.innerHTML = `
      <div class="rank-badge ${currentBadge.class}">
        <span class="badge-icon">${currentBadge.icon}</span>
        <span class="badge-name">${currentBadge.name}</span>
      </div>
      <div class="badge-info-btn">i</div>
      <div class="badge-tooltip">
        <h4>🏆 Donor Rank System</h4>
        <div class="badge-criteria">
          ${BADGE_RANKS.map((rank, index) => {
            const isAchieved = totalDonations >= rank.threshold;
            const isCurrent = rank.name === currentBadge.name;
            const progress = Math.min((totalDonations / rank.threshold) * 100, 100);
            
            return `
              <div class="criteria-item ${rank.class.replace('badge-', '')}" style="opacity: ${isAchieved ? 1 : 0.6};">
                <span class="criteria-icon">${rank.icon}</span>
                <div style="flex: 1;">
                  <div class="criteria-text">
                    <strong style="color: ${rank.color};">${rank.name}</strong>
                    ${isCurrent ? '<span style="color:#00ff87;"> ✓ Current</span>' : ''}
                    ${!isAchieved && index > 0 ? '<span style="color:#ff006e;"> 🔒 Locked</span>' : ''}
                  </div>
                  ${!isAchieved ? `
                    <div style="margin-top:4px;width:100%;height:4px;background:rgba(255,255,255,0.1);border-radius:2px;overflow:hidden;">
                      <div style="width:${progress}%;height:100%;background:${rank.color};"></div>
                    </div>
                  ` : ''}
                </div>
                <span class="criteria-amount">${formatINR(rank.threshold)}</span>
              </div>
            `;
          }).join('')}
        </div>
        <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(139,92,246,0.3);text-align:center;">
          <p style="font-size:12px;color:#94a3b8;margin:0;">
            Your Progress: <strong style="color:#00ff87;">${formatINR(totalDonations)}</strong>
          </p>
        </div>
      </div>
    `;
  } else {
    // No badge yet - show progress to first badge
    const firstBadge = BADGE_RANKS[0];
    const progress = (totalDonations / firstBadge.threshold) * 100;
    const remaining = firstBadge.threshold - totalDonations;
    
    badgeContainer.innerHTML = `
      <div class="rank-badge" style="background:rgba(139,92,246,0.2);border:2px dashed #8b5cf6;animation:none;">
        <span class="badge-icon">🎯</span>
        <span class="badge-name">New Donor</span>
      </div>
      <div class="badge-info-btn">i</div>
      <div class="badge-tooltip">
        <h4>🏆 Donor Rank System</h4>
        <p style="color:#94a3b8;font-size:13px;margin-bottom:16px;">
          Earn badges by making donations! Your first rank is just <strong style="color:#00ff87;">${formatINR(remaining)}</strong> away!
        </p>
        <div style="margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-size:12px;color:#94a3b8;">Progress to ${firstBadge.icon} ${firstBadge.name}</span>
            <span style="font-size:12px;color:#fff;font-weight:700;">${progress.toFixed(1)}%</span>
          </div>
          <div style="width:100%;height:8px;background:rgba(255,255,255,0.1);border-radius:4px;overflow:hidden;">
            <div style="width:${progress}%;height:100%;background:linear-gradient(90deg, #ff006e 0%, #8b5cf6 100%);transition:width 0.5s ease;"></div>
          </div>
        </div>
        <div class="badge-criteria">
          ${BADGE_RANKS.map(rank => `
            <div class="criteria-item ${rank.class.replace('badge-', '')}" style="opacity: 0.6;">
              <span class="criteria-icon">${rank.icon}</span>
              <div class="criteria-text"><strong style="color: ${rank.color};">${rank.name}</strong></div>
              <span class="criteria-amount">${formatINR(rank.threshold)}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
}

/* --- Fetch Causes from Backend --- */
async function fetchCauses() {
  try {
    const res = await fetch("/causes");
    const data = await res.json();
    causes = data;
    renderCauses();
    updateStats();
  } catch (err) {
    console.error("Error fetching causes:", err);
    causesGrid.innerHTML = "<p class='muted'>Unable to load causes at the moment.</p>";
  }
}

/* --- Render Causes with Smooth Animations --- */
function renderCauses() {
  causesGrid.innerHTML = "";
  causes.forEach((cause, index) => {
    const percent = Math.min((cause.raised / cause.goal) * 100, 100).toFixed(1);
    const remaining = Math.max(0, cause.goal - cause.raised);
    const isFullyFunded = remaining <= 0;
    
    const card = document.createElement("div");
    card.className = "cause-card card";
    card.style.animationDelay = `${index * 0.1}s`;
    
    const buttonHTML = isFullyFunded 
      ? `<button class="fund-btn" data-id="${cause.id}" style="background:#00ff87;cursor:not-allowed;" disabled>✅ Goal Reached!</button>`
      : `<button class="fund-btn" data-id="${cause.id}">Fund Cause</button>`;
    
    const statusText = isFullyFunded
      ? `<p class="muted small" style="color:#00ff87;font-weight:600;">🎉 ${formatINR(cause.raised)} raised - Goal reached!</p>`
      : `<p class="muted small">${formatINR(cause.raised)} raised of ${formatINR(cause.goal)} <span style="color:#ff006e;">(₹${remaining} remaining)</span></p>`;
    
    const ngoLabel = cause.ngo_name ? `
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
        <span style="background:linear-gradient(135deg,#8b5cf6,#ff006e);padding:4px 12px;border-radius:12px;font-size:11px;font-weight:700;text-transform:uppercase;">🏢 ${cause.ngo_name}</span>
      </div>
    ` : '';
    
    card.innerHTML = `
      <img src="${cause.image}" alt="${cause.title}" class="cause-img">
      ${ngoLabel}
      <h3>${cause.title}</h3>
      <p style="font-size:14px;line-height:1.6;color:#94a3b8;">${cause.description}</p>
      <div class="progress-wrap-small">
        <div class="progress-small-fill" style="width:0%;"></div>
      </div>
      ${statusText}
      ${buttonHTML}
    `;
    causesGrid.appendChild(card);
    
    // Animate progress bar with delay
    setTimeout(() => {
      const progressBar = card.querySelector('.progress-small-fill');
      if (progressBar) {
        progressBar.style.width = `${percent}%`;
      }
    }, 100 + (index * 100));
  });

  document.querySelectorAll(".fund-btn:not([disabled])").forEach((btn) => {
    btn.addEventListener("click", handleFundClick);
  });

  causesSupportedEl.textContent = supportedCauses.size;
}

/* --- Handle Funding - Show Modal --- */
async function handleFundClick(e) {
  const button = e.target;
  const id = Number(button.getAttribute("data-id"));
  selectedCause = causes.find((c) => c.id === id);
  
  // Check if cause was found
  if (!selectedCause) {
    alert('❌ Cause not found. Please refresh the page and try again.');
    console.error('Cause not found with id:', id);
    console.log('Available causes:', causes);
    return;
  }
  
  const goal = selectedCause.goal || 0;
  const raised = selectedCause.raised || 0;
  const remaining = Math.max(0, goal - raised);
  
  // Show modal
  document.getElementById('fundingModal').style.display = 'block';
  
  // Set cause name with NGO label if available
  const causeNameEl = document.getElementById('modalCauseName');
  if (selectedCause.ngo_name) {
    causeNameEl.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:6px;">
        <span style="font-size:12px;color:#8b5cf6;font-weight:600;">🏢 ${selectedCause.ngo_name}</span>
        <span>${selectedCause.title}</span>
      </div>
    `;
  } else {
    causeNameEl.textContent = selectedCause.title;
  }
  
  document.getElementById('modalWallet').textContent = user.walletAddress || "Not connected";
  document.getElementById('modalGoal').textContent = formatINR(goal);
  document.getElementById('modalRaised').textContent = formatINR(raised);
  document.getElementById('modalRemaining').textContent = formatINR(remaining);
  document.getElementById('donationAmount').value = '';
  document.getElementById('donationAmount').max = remaining; // Set max attribute
  document.getElementById('modalAmount').textContent = '₹0';
  document.getElementById('modalImpact').textContent = '0 lives';
  document.getElementById('confirmCheckbox').checked = false;
  document.getElementById('confirmBtn').disabled = true;
  document.getElementById('donationError').style.display = 'none';
  
  // Check if cause is fully funded
  if (remaining <= 0) {
    document.getElementById('donationAmount').disabled = true;
    document.getElementById('donationAmount').placeholder = 'Goal already reached!';
    document.getElementById('donationError').textContent = '✅ This cause has reached its funding goal!';
    document.getElementById('donationError').style.color = '#00ff87';
    document.getElementById('donationError').style.display = 'block';
  } else {
    document.getElementById('donationAmount').disabled = false;
    document.getElementById('donationAmount').placeholder = `Max: ₹${remaining}`;
  }
}

/* --- Close Modal --- */
function closeFundingModal() {
  document.getElementById('fundingModal').style.display = 'none';
  selectedCause = null;
}

/* --- Handle Amount Input --- */
document.addEventListener('DOMContentLoaded', () => {
  const amountInput = document.getElementById('donationAmount');
  const confirmCheckbox = document.getElementById('confirmCheckbox');
  const confirmBtn = document.getElementById('confirmBtn');
  
  if (amountInput) {
    amountInput.addEventListener('input', (e) => {
      const amount = Number(e.target.value);
      const errorDiv = document.getElementById('donationError');
      
      if (amount > 0) {
        document.getElementById('modalAmount').textContent = formatINR(amount);
        const lives = Math.floor(amount / livesPer25);
        document.getElementById('modalImpact').textContent = `~${lives} ${lives === 1 ? 'life' : 'lives'} impacted`;
        
        // Validate against remaining amount
        if (selectedCause) {
          const goal = selectedCause.goal || 0;
          const raised = selectedCause.raised || 0;
          const remaining = Math.max(0, goal - raised);
          
          if (amount > remaining) {
            errorDiv.textContent = `⚠️ Amount exceeds remaining limit! Maximum: ₹${remaining}`;
            errorDiv.style.color = '#ff006e';
            errorDiv.style.display = 'block';
          } else {
            errorDiv.style.display = 'none';
          }
        }
      } else {
        document.getElementById('modalAmount').textContent = '₹0';
        document.getElementById('modalImpact').textContent = '0 lives';
        errorDiv.style.display = 'none';
      }
      updateConfirmButton();
    });
  }
  
  if (confirmCheckbox) {
    confirmCheckbox.addEventListener('change', updateConfirmButton);
  }
});

function updateConfirmButton() {
  const amount = Number(document.getElementById('donationAmount').value);
  const checked = document.getElementById('confirmCheckbox').checked;
  
  // Check if amount exceeds remaining
  let isValid = amount > 0 && checked;
  if (selectedCause && amount > 0) {
    const goal = selectedCause.goal || 0;
    const raised = selectedCause.raised || 0;
    const remaining = Math.max(0, goal - raised);
    if (amount > remaining) {
      isValid = false;
    }
  }
  
  document.getElementById('confirmBtn').disabled = !isValid;
}

/* --- Confirm Donation --- */
async function confirmDonation() {
  const amount = Number(document.getElementById('donationAmount').value);
  
  // Validate amount and selectedCause
  if (!amount || amount <= 0) {
    alert('❌ Please enter a valid donation amount');
    return;
  }
  
  if (!selectedCause) {
    alert('❌ No cause selected. Please try again.');
    closeFundingModal();
    return;
  }
  
  // Store cause data before async operations (to prevent null issues)
  const causeData = {
    id: selectedCause.id,
    title: selectedCause.title,
    goal: selectedCause.goal || 0,
    raised: selectedCause.raised || 0
  };
  
  // Final validation against remaining amount
  const remaining = Math.max(0, causeData.goal - causeData.raised);
  
  if (amount > remaining) {
    alert(`❌ Donation amount (₹${amount.toLocaleString()}) exceeds the remaining needed amount (₹${remaining.toLocaleString()}). Please enter a valid amount.`);
    return;
  }
  
  const confirmBtn = document.getElementById('confirmBtn');
  confirmBtn.disabled = true;
  confirmBtn.textContent = '⏳ Processing...';
  
  try {
    // Get blockchain user credentials
    const blockchainUser = localStorage.getItem('blockchainUser');
    if (!blockchainUser) {
      throw new Error('User not logged in. Please login again.');
    }
    
    const userData = JSON.parse(blockchainUser);
    
    // Prompt for password for security
    const password = prompt('🔐 Enter your password to confirm donation:');
    if (!password) {
      confirmBtn.disabled = false;
      confirmBtn.textContent = 'Confirm Transaction';
      return; // User cancelled
    }
    
    confirmBtn.textContent = '💰 Processing INR Blockchain Transaction...';
    
    // Call INR blockchain donation API
    const response = await fetch('/api/blockchain/donate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: userData.email,
        password: password,
        cause_id: causeData.id,
        amount: amount
      })
    });
    
    const result = await response.json();
    
    if (!result.success) {
      throw new Error(result.error || 'Donation failed');
    }
    
    confirmBtn.textContent = '✅ Transaction Complete!';
    
    // Update local state
    window.totalImpact += amount;
    window.donationsMade++;
    window.livesImpacted += Math.floor(amount / livesPer25);
    window.supportedCauses.add(causeData.title);
    
    // Store transaction locally
    const transactionKey = `transactions_${user.walletAddress}`;
    const transactions = JSON.parse(localStorage.getItem(transactionKey) || '[]');
    transactions.unshift({
      id: result.transaction_id,
      cause: causeData.title,
      amount: amount,
      timestamp: result.timestamp,
      wallet: user.walletAddress,
      status: 'confirmed',
      txHash: result.transaction_id,
      blockchain: true,
      block_number: result.block_number
    });
    localStorage.setItem(transactionKey, JSON.stringify(transactions));
    
    // Update wallet balance display
    updateWalletBalance();
    
    // Add to recent donations
    addRecentDonation(causeData.title, amount);
    
    // Close modal first
    closeFundingModal();
    
    // Show success message
    alert(`✅ DONATION SUCCESSFUL!\n\n💰 Amount: ₹${amount.toLocaleString()}\n📝 Cause: ${causeData.title}\n🔗 Transaction ID: ${result.transaction_id.substring(0, 16)}...\n📦 Recorded on INR Blockchain!\n💵 Deducted from your wallet\n\n📥 Receipt available in Transaction History.`);
    
    // Refresh the page to update all data (wallet balance, causes, etc.)
    window.location.reload();
    
  } catch (error) {
    console.error('❌ Donation failed:', error);
    confirmBtn.disabled = false;
    confirmBtn.textContent = 'Confirm Transaction';
    alert(error.message || '❌ Donation failed. Please try again.');
  }
}

/* --- Stats Update with Smooth Animations --- */
function updateStats() {
  // Animate number changes
  animateNumber(totalImpactEl, window.totalImpact, formatINR);
  animateNumber(donationsMadeEl, window.donationsMade);
  animateNumber(livesImpactedEl, window.livesImpacted);
  causesSupportedEl.textContent = window.supportedCauses.size;

  const avgProgress =
    causes.reduce((sum, c) => sum + (c.raised / c.goal) * 100, 0) / causes.length || 0;
  const percent = Math.min(avgProgress, 100).toFixed(1);
  
  // Smooth progress bar animation
  setTimeout(() => {
  impactProgressBar.style.width = `${percent}%`;
  impactPercent.textContent = `${percent}%`;
  }, 100);
  
  // Update badge based on new total
  renderBadge();
  
  // Save user data whenever stats are updated
  saveUserData();
}

/* --- Animate Numbers --- */
function animateNumber(element, targetValue, formatter = null) {
  const currentValue = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
  const duration = 800;
  const steps = 30;
  const increment = (targetValue - currentValue) / steps;
  let current = currentValue;
  let step = 0;

  const timer = setInterval(() => {
    step++;
    current += increment;
    
    if (step >= steps) {
      current = targetValue;
      clearInterval(timer);
    }
    
    element.textContent = formatter ? formatter(Math.floor(current)) : Math.floor(current);
  }, duration / steps);
}

/* --- Recent Donations with Animation --- */
function addRecentDonation(title, amount) {
  // Remove "No donations yet" message if present
  const noDonatonsMsg = recentList.querySelector('.muted');
  if (noDonatonsMsg) {
    noDonatonsMsg.remove();
  }

  const li = document.createElement("li");
  li.textContent = `Funded ${formatINR(amount)} to "${title}"`;
  li.style.animation = 'none';
  recentList.prepend(li);
  
  // Add to recentDonations array
  window.recentDonations.unshift({ causeName: title, amount: amount, timestamp: new Date().toISOString() });
  if (window.recentDonations.length > 6) {
    window.recentDonations.pop();
  }
  
  // Trigger animation
  setTimeout(() => {
    li.style.animation = '';
  }, 10);

  if (recentList.children.length > 6) {
    const lastItem = recentList.lastChild;
    lastItem.style.transition = 'all 0.3s ease';
    lastItem.style.opacity = '0';
    lastItem.style.transform = 'translateX(-20px)';
    setTimeout(() => {
      recentList.removeChild(lastItem);
    }, 300);
  }
  
  // Save user data whenever recent donations are updated
  saveUserData();
}

/* --- Render Recent Donations from Saved Data --- */
function renderRecentDonations() {
  if (!window.recentDonations || window.recentDonations.length === 0) {
    return; // Keep default "No donations yet" message
  }
  
  // Remove "No donations yet" message
  const noDonatonsMsg = recentList.querySelector('.muted');
  if (noDonatonsMsg) {
    noDonatonsMsg.remove();
  }
  
  // Clear list
  recentList.innerHTML = '';
  
  // Render saved donations
  window.recentDonations.forEach(donation => {
    const li = document.createElement("li");
    li.textContent = `Funded ${formatINR(donation.amount)} to "${donation.causeName}"`;
    recentList.appendChild(li);
  });
}

/* --- Add Success Animation to Donation --- */
function showSuccessAnimation(button) {
  const originalText = button.textContent;
  button.textContent = '✓ Funded!';
  button.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
  
  setTimeout(() => {
    button.textContent = originalText;
  }, 2000);
}

/* --- Logout Functionality --- */
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", async () => {
    try {
      // Clear session storage (temporary data)
      sessionStorage.clear();
      
      // Keep all user data for all wallets (keys starting with 'transactions_', 'userData_', or 'userProfile_')
      const itemsToKeep = {};
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.startsWith('transactions_') || key.startsWith('userData_') || key.startsWith('userProfile_'))) {
          itemsToKeep[key] = localStorage.getItem(key);
        }
      }
      
      // Clear all localStorage
      localStorage.clear();
      
      // Restore all transaction histories
      Object.keys(itemsToKeep).forEach(key => {
        localStorage.setItem(key, itemsToKeep[key]);
      });
      
      // Request MetaMask to disconnect (revoke permissions)
      if (window.ethereum && window.ethereum.request) {
        try {
          // This will prompt user to disconnect on next connection
          await window.ethereum.request({
            method: "wallet_revokePermissions",
            params: [{ eth_accounts: {} }]
          });
        } catch (err) {
          console.log('MetaMask disconnect:', err.message);
        }
      }
      
      // Redirect to logout endpoint
      window.location.href = "/donator-logout";
      
    } catch (error) {
      console.error('Logout error:', error);
      // Fallback: just redirect
      window.location.href = "/donator-logout";
    }
  });
}

/* --- Transaction History --- */
function getTransactionKey() {
  // Get wallet-specific key for transactions
  return `transactions_${user.walletAddress}`;
}

function renderTransactionHistory() {
  const transactions = JSON.parse(localStorage.getItem(getTransactionKey()) || '[]');
  const container = document.getElementById('transactionList');
  
  if (transactions.length === 0) {
    container.innerHTML = '<p class="muted">No transactions yet</p>';
    return;
  }
  
  container.innerHTML = transactions.map(t => {
    const date = new Date(t.timestamp);
    const blockchainBadge = t.blockchain ? 
      `<span style="background:#10b981;color:white;padding:4px 10px;border-radius:12px;font-size:11px;font-weight:600;display:inline-block;margin-left:8px;">⛓️ BLOCKCHAIN VERIFIED</span>` : 
      `<span style="background:#6b7280;color:white;padding:4px 10px;border-radius:12px;font-size:11px;font-weight:600;display:inline-block;margin-left:8px;">📝 DEMO MODE</span>`;
    
    const txHashInfo = t.txHash ? 
      `<div class="transaction-meta" style="color:#10b981;font-family:monospace;font-size:11px;">
        Tx: ${t.txHash.slice(0, 16)}...${t.txHash.slice(-10)}
      </div>` : '';
    
    return `
      <div class="transaction-item">
        <div class="transaction-info">
          <h4>${t.cause} ${blockchainBadge}</h4>
          <div class="transaction-meta">
            ${date.toLocaleDateString()} at ${date.toLocaleTimeString()}
          </div>
          <div class="transaction-meta">
            Wallet: ${t.wallet.slice(0, 10)}...${t.wallet.slice(-8)}
          </div>
          ${txHashInfo}
          <div class="transaction-actions">
            <button class="btn-receipt" onclick="downloadReceipt(${t.id})">📥 Download Receipt</button>
          </div>
        </div>
        <div class="transaction-amount">${formatINR(t.amount)}</div>
      </div>
    `;
  }).join('');
}

/* --- Receipt Generation --- */
function downloadReceipt(transactionId) {
  const transactions = JSON.parse(localStorage.getItem(getTransactionKey()) || '[]');
  const transaction = transactions.find(t => t.id === transactionId);
  
  if (!transaction) {
    alert('Transaction not found');
    return;
  }
  
  const date = new Date(transaction.timestamp);
  
  // Use jsPDF to generate PDF
  try {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'pt', 'a4');
    
    // Page dimensions
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 40;
    let y = margin;
    
    // Add colored header background
    doc.setFillColor(139, 92, 246); // Purple
    doc.rect(0, 0, pageWidth, 140, 'F');
    
    // Title
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(32);
    doc.setFont('helvetica', 'bold');
    doc.text('ImpactEcho', pageWidth / 2, y + 40, { align: 'center' });
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'normal');
    doc.text('Amplifying Generosity Worldwide', pageWidth / 2, y + 65, { align: 'center' });
    
    y = 160;
    
    // Receipt title
    doc.setTextColor(26, 11, 46);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('DONATION RECEIPT', pageWidth / 2, y, { align: 'center' });
    
    doc.setFontSize(12);
    doc.setTextColor(139, 92, 246);
    doc.setFont('courier', 'bold');
    doc.text(`Receipt #${transaction.id}`, pageWidth / 2, y + 25, { align: 'center' });
    
    y += 60;
    
    // Add horizontal line
    doc.setDrawColor(139, 92, 246);
    doc.setLineWidth(2);
    doc.line(margin, y, pageWidth - margin, y);
    
    y += 30;
    
    // Transaction details
    doc.setTextColor(50, 50, 50);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    
    // Left column
    doc.text('TRANSACTION DATE:', margin, y);
    doc.setFont('helvetica', 'normal');
    doc.text(date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }), margin, y + 15);
    
    // Right column
    doc.setFont('helvetica', 'bold');
    doc.text('TRANSACTION TIME:', pageWidth / 2 + 20, y);
    doc.setFont('helvetica', 'normal');
    doc.text(date.toLocaleTimeString('en-US'), pageWidth / 2 + 20, y + 15);
    
    y += 50;
    
    // Cause
    doc.setFont('helvetica', 'bold');
    doc.text('CAUSE/PROJECT:', margin, y);
    doc.setFont('helvetica', 'normal');
    const causeLines = doc.splitTextToSize(transaction.cause, pageWidth - margin * 2);
    doc.text(causeLines, margin, y + 15);
    
    y += 15 + (causeLines.length * 12) + 20;
    
    // Wallet address
    doc.setFont('helvetica', 'bold');
    doc.text('DONOR WALLET ADDRESS:', margin, y);
    doc.setFont('courier', 'normal');
    doc.setFontSize(9);
    doc.text(transaction.wallet, margin, y + 15);
    doc.setFontSize(10);
    
    y += 50;
    
    // Amount box
    doc.setFillColor(139, 92, 246);
    doc.roundedRect(margin, y, pageWidth - margin * 2, 70, 10, 10, 'F');
    
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('TOTAL DONATION AMOUNT', pageWidth / 2, y + 25, { align: 'center' });
    
    doc.setFontSize(28);
    doc.setFont('helvetica', 'bold');
    doc.text(formatINR(transaction.amount), pageWidth / 2, y + 55, { align: 'center' });
    
    y += 90;
    
    // Blockchain info
    if (transaction.blockchain && transaction.txHash) {
      doc.setFillColor(16, 185, 129); // Green
      doc.roundedRect(margin, y, pageWidth - margin * 2, 80, 10, 10, 'F');
      
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('⛓ BLOCKCHAIN VERIFIED DONATION', pageWidth / 2, y + 25, { align: 'center' });
      
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');
      doc.text('This transaction has been permanently recorded on the blockchain', pageWidth / 2, y + 42, { align: 'center' });
      
      doc.setFont('courier', 'bold');
      doc.setFontSize(7);
      const txHashLines = doc.splitTextToSize(`TX: ${transaction.txHash}`, pageWidth - margin * 2 - 40);
      doc.text(txHashLines, pageWidth / 2, y + 60, { align: 'center' });
      
      y += 95;
    } else {
      doc.setFillColor(107, 114, 128); // Gray
      doc.roundedRect(margin, y, pageWidth - margin * 2, 35, 10, 10, 'F');
      
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text('📝 Demo Mode - Enable local blockchain for verified transactions', pageWidth / 2, y + 22, { align: 'center' });
      
      y += 50;
    }
    
    // Verification ID
    doc.setDrawColor(139, 92, 246);
    doc.setLineWidth(1);
    doc.setLineDash([5, 3]);
    doc.roundedRect(margin, y, pageWidth - margin * 2, 40, 8, 8, 'D');
    doc.setLineDash([]);
    
    doc.setTextColor(100, 100, 100);
    doc.setFontSize(8);
    doc.setFont('helvetica', 'bold');
    doc.text('RECEIPT ID:', margin + 15, y + 18);
    
    doc.setFont('courier', 'bold');
    doc.setFontSize(10);
    doc.setTextColor(26, 11, 46);
    doc.text(`${transaction.id}-${Date.now().toString(36).toUpperCase()}`, margin + 15, y + 32);
    
    y += 60;
    
    // Footer
    if (y + 100 > pageHeight - margin) {
      doc.addPage();
      y = margin;
    }
    
    doc.setFillColor(248, 249, 250);
    doc.rect(0, pageHeight - 120, pageWidth, 120, 'F');
    
    doc.setTextColor(139, 92, 246);
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text('Thank You for Your Generosity! 🙏', pageWidth / 2, pageHeight - 85, { align: 'center' });
    
    doc.setTextColor(100, 100, 100);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text('Your contribution will make a real difference in someone\'s life.', pageWidth / 2, pageHeight - 65, { align: 'center' });
    
    doc.setFontSize(8);
    doc.text('This receipt is electronically generated and valid without signature.', pageWidth / 2, pageHeight - 35, { align: 'center' });
    doc.text(`© ${new Date().getFullYear()} ImpactEcho · All rights reserved`, pageWidth / 2, pageHeight - 20, { align: 'center' });
    
    // Save the PDF
    doc.save(`ImpactEcho-Receipt-${transaction.id}.pdf`);
    
    alert('✅ Receipt downloaded as PDF successfully!');
  } catch (error) {
    console.error('PDF generation error:', error);
    alert('❌ Error generating PDF. Please try again.');
  }
}

/* --- Profile Management --- */
function showEditProfileModal() {
  const modal = document.getElementById('editProfileModal');
  if (!modal) {
    alert('Profile editing not available on this page');
    return;
  }
  
  // Pre-fill with current profile data
  const profile = getUserProfile(user.walletAddress);
  if (profile) {
    document.getElementById('editProfileName').value = profile.name || '';
    document.getElementById('editProfileEmail').value = profile.email || '';
  }
  
  modal.style.display = 'flex';
}

function closeEditProfileModal() {
  const modal = document.getElementById('editProfileModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

function saveUserProfile(walletAddress, name, email) {
  const profileKey = `userProfile_${walletAddress}`;
  const profile = {
    name: name,
    email: email || '',
    walletAddress: walletAddress,
    updatedAt: new Date().toISOString()
  };
  localStorage.setItem(profileKey, JSON.stringify(profile));
  return profile;
}

function updateProfile() {
  const nameInput = document.getElementById('editProfileName');
  const emailInput = document.getElementById('editProfileEmail');
  
  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  
  if (!name) {
    alert('Please enter your name');
    return;
  }
  
  // Save profile
  saveUserProfile(user.walletAddress, name, email);
  
  // Update display
  user.username = name;
  user.email = email;
  renderUsername();
  
  // Close modal
  closeEditProfileModal();
  
  alert(`✅ Profile updated successfully!`);
  
  // Reload page to reflect changes everywhere
  setTimeout(() => location.reload(), 500);
}

/* --- Add Money Feature --- */
function showAddMoneyModal() {
  const modal = document.getElementById('addMoneyModal');
  if (!modal) {
    alert('Add Money feature not available');
    return;
  }
  
  // Update current balance display
  const currentBalance = parseFloat(document.getElementById('walletBalance').textContent.replace('₹', '').replace(/,/g, '')) || 0;
  document.getElementById('currentBalanceDisplay').textContent = `₹${currentBalance.toLocaleString()}`;
  
  // Clear previous selections
  document.getElementById('customAddAmount').value = '';
  document.querySelectorAll('.amount-btn').forEach(btn => btn.classList.remove('selected'));
  document.getElementById('addMoneyError').style.display = 'none';
  document.getElementById('addMoneySuccess').style.display = 'none';
  
  modal.style.display = 'flex';
}

function closeAddMoneyModal() {
  const modal = document.getElementById('addMoneyModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

function selectAddAmount(amount) {
  // Highlight selected button
  document.querySelectorAll('.amount-btn').forEach(btn => btn.classList.remove('selected'));
  event.target.classList.add('selected');
  
  // Clear custom input
  document.getElementById('customAddAmount').value = '';
}

async function addMoneyToWallet() {
  const customInput = document.getElementById('customAddAmount');
  const errorDiv = document.getElementById('addMoneyError');
  const successDiv = document.getElementById('addMoneySuccess');
  
  // Get selected amount
  const selectedBtn = document.querySelector('.amount-btn.selected');
  let amount = 0;
  
  if (customInput.value) {
    amount = parseFloat(customInput.value);
  } else if (selectedBtn) {
    amount = parseFloat(selectedBtn.textContent.replace('₹', '').replace(/,/g, ''));
  }
  
  if (!amount || amount < 100) {
    errorDiv.textContent = '❌ Please enter an amount of at least ₹100';
    errorDiv.style.display = 'block';
    successDiv.style.display = 'none';
    return;
  }
  
  try {
    const response = await fetch('/api/blockchain/add-money', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        address: user.walletAddress,
        amount: amount
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      successDiv.textContent = `✅ Successfully added ₹${amount.toLocaleString()} to your wallet!`;
      successDiv.style.display = 'block';
      errorDiv.style.display = 'none';
      
      // Update wallet balance display
      document.getElementById('walletBalance').textContent = `₹${result.new_balance.toLocaleString()}`;
      document.getElementById('currentBalanceDisplay').textContent = `₹${result.new_balance.toLocaleString()}`;
      
      // Close modal after 1.5 seconds
      setTimeout(() => {
        closeAddMoneyModal();
        location.reload(); // Refresh to show updated balance everywhere
      }, 1500);
    } else {
      errorDiv.textContent = `❌ ${result.error || 'Failed to add money'}`;
      errorDiv.style.display = 'block';
      successDiv.style.display = 'none';
    }
  } catch (error) {
    console.error('Error adding money:', error);
    errorDiv.textContent = '❌ Network error. Please try again.';
    errorDiv.style.display = 'block';
    successDiv.style.display = 'none';
  }
}

// Update wallet balance on page load
async function updateWalletBalance() {
  try {
    const response = await fetch('/api/blockchain/balance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address: user.walletAddress })
    });
    
    const result = await response.json();
    
    if (result.success) {
      document.getElementById('walletBalance').textContent = `₹${result.wallet_balance.toLocaleString()}`;
    }
  } catch (error) {
    console.error('Error fetching wallet balance:', error);
  }
}

/* --- Initialize --- */
function init() {
  renderUsername();
  loadUserData(); // Load saved user data first
  updateWalletBalance(); // Load wallet balance
  fetchCauses();
  renderTransactionHistory();
}

document.addEventListener("DOMContentLoaded", init);

