// 施術者情報はこのファイルだけを編集してください。
// 写真を変更するときは image のURL（または images/... のパス）を書き換えます。
const staffMembers = [
  {
    id: "staff1",
    name: "院長　保坂 浩之",
    cardName: "保坂 浩之",
    image: "https://picsum.photos/seed/staff1/600/400",
    groups: [
      { label: "施術歴", items: ["18年"] },
      { label: "職歴", items: ["木下サーカス（音響照明・空中ブランコ）", "機能訓練指導員"] },
      { label: "免許", items: ["はり師", "きゅう師", "あん摩マッサージ指圧師"] },
      { label: "所属・認定・研修", items: [
        "経絡治療学会　所属　【10年表彰】",
        "全日本鍼灸学会　所属　【認定鍼灸師】",
        { main: "日本パーキンソン病・運動障害疾患学会　所属", note: "【認定パーキンソン病療養指導士】" },
        "日本栄養精神医学会　所属",
        "分子栄養医学研究所　所属",
        "あん摩・マッサージ・指圧師、はり師およびきゅう師 臨床実習指導者講習　【修了】",
        "地域医療連携講座診察学　【修了】",
        "発達障害専門支援士",
        "強度行動障害研修　【修了】"
      ] },
      { label: "専門", items: [
        "脈を診て身体の不調を探し、ツボへ鍼を打つ伝統的な日本鍼灸",
        "関節の運動性に着目したマッサージ施術",
        "パーキンソン病や小脳失調などに対する運動療法",
        "生活習慣から遡り、栄養療法に基づいたご提案"
      ] }
    ]
  },
  {
    id: "staff2",
    name: "小川 大空",
    cardName: "小川 大空",
    image: "https://picsum.photos/seed/staff2/600/400",
    groups: [
      { label: "経歴", items: ["心理学部心理学科卒業", "介護士", "機能訓練指導員"] },
      { label: "資格・所属", items: [
        "はり師",
        "きゅう師",
        "あん摩マッサージ指圧師",
        "日本メディカル美容鍼協会　所属　【認定美容鍼灸師】",
        "介護福祉士",
        "日本心理学会　所属　【認定心理士】"
      ] }
    ],
    message: "介護現場で培った経験から、身体機能の維持・改善だけでなく、ご本人の自立した生活やご家族の介護負担の軽減も見据えた施術を大切にしています。介護福祉士・認定心理士として、身体と心の両面から、一人ひとりに寄り添います。"
  }
];

const escapeHtml = value => String(value).replace(/[&<>"']/g, character => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
}[character]));

const renderStaffDetail = member => {
  const renderItem = item => {
    if (typeof item === "string") return escapeHtml(item);
    return `<span>${escapeHtml(item.main)}</span><span class="staff-profile-subitem">${escapeHtml(item.note)}</span>`;
  };
  const groups = member.groups.map(group => `
    <section class="staff-profile-group">
      <h4>${escapeHtml(group.label)}</h4>
      <ul>${group.items.map(item => `<li>${renderItem(item)}</li>`).join("")}</ul>
    </section>`).join("");
  const message = member.message ? `
    <section class="staff-profile-group staff-profile-message">
      <h4>ごあいさつ</h4><p>${escapeHtml(member.message)}</p>
    </section>` : "";
  return groups + message;
};

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
    document.getElementById("modal-detail").innerHTML = renderStaffDetail(member);
    document.getElementById("modal-img").src = member.image;
    modal.hidden = false; modal.classList.add("show");
  });
  document.getElementById("staff-modal-close").addEventListener("click", close);
  modal.addEventListener("click", event => { if (event.target === modal) close(); });
  document.addEventListener("keydown", event => { if (event.key === "Escape") close(); });
});
