function restoreHtmlDelimiters(guideLeftValues) {
  try {
    const targetDiv = document.querySelector(".rg-overlay");

    if (!targetDiv) {
      alert("Could not find div with class 'rg-overlay'");
      return;
    }

    // Clear existing guides
    const existingGuides = targetDiv.querySelectorAll(".guide.v.draggable");
    // alert("Found " + existingGuides.length + " existing guides");
    existingGuides.forEach((guide) => guide.remove());

    // Add new guides from the list
    guideLeftValues.forEach((leftValue, index) => {
      const guide = document.createElement("div");
      guide.className = "guide v draggable";
      guide.id = `guide-${index}`;
      guide.style.left = `${leftValue}px`;
      guide.style.top = `0px`;

      const info = document.createElement("div");
      info.className = "info";
      info.style.top = "347px";
      info.style.display = "none";
      info.textContent = `${leftValue}px`;

      guide.appendChild(info);
      targetDiv.appendChild(guide);
    });

    // alert("Restored " + guideLeftValues.length + " guide(s)");
  } catch (error) {
    alert("Error restoring HTML state: " + error.message);
  }
}

const restoreHtmlTableArea = (tableArea) => {
  const rectangle = document.getElementById("absoluteBox");
  // Set left and top via style
  rectangle.style.left = `${tableArea.left}px`;
  rectangle.style.top = `${tableArea.top}px`;
  rectangle.style.width = `${tableArea.width}px`;
  rectangle.style.height = `${tableArea.height}px`;
};

const restoreBreakLines = (value) => {
  const checkBox = document.getElementById("breakLinesCheckbox");
  checkBox.checked = value == 1; // convert 1 to true, 0 to false
};
