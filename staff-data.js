// 施術者情報はこのファイルだけを編集してください。
const staffMembers = [
  { id: "staff1", name: "院長　保坂 浩之", cardName: "保坂 浩之", image: "https://picsum.photos/seed/staff1/600/400", detail: "・生年月：1985年4月<br>・資格：はり師・きゅう師・あん摩マッサージ指圧師<br>・専門：" },
  { id: "staff2", name: "小川 大空", cardName: "小川 大空", image: "https://picsum.photos/seed/staff2/600/400", detail: "・生年月：1997年8月<br>・資格：はり師・きゅう師・あん摩マッサージ指圧師<br>・専門：" },
  { id: "staff3", name: "coming soon", cardName: "coming soon", image: "https://picsum.photos/seed/staff3/600/400", detail: "・資格：はり師・きゅう師<br>・専門：" }
];

document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("staff-grid");
  const modal = document.getElementById("staff-modal");
  if (!grid || !modal) return;
  grid.innerHTML = staffMembers.map(member => `<button type="button" class="staff-card" data-staff-id="${member.id}"><img src="${member.image}" alt="${member.cardName}の写真" loading="lazy"><span class="staff-name">${member.cardName}</span></button>`).join("");
  const close = () => { modal.classList.remove("show"); modal.hidden = true; };
  grid.addEventListener("click", event => {
    const card = event.target.closest("[data-staff-id]"); if (!card) return;
    const member = staffMembers.find(item => item.id === card.dataset.staffId); if (!member) return;
    document.getElementById("modal-name").textContent = member.name;
    document.getElementById("modal-detail").innerHTML = member.detail;
    document.getElementById("modal-img").src = member.image;
    modal.hidden = false; modal.classList.add("show");
  });
  document.getElementById("staff-modal-close").addEventListener("click", close);
  modal.addEventListener("click", event => { if (event.target === modal) close(); });
  document.addEventListener("keydown", event => { if (event.key === "Escape") close(); });
});
