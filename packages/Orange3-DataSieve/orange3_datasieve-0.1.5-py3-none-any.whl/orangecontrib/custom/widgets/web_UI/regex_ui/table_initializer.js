const highlight = (element, matches) => {
  if (!matches || matches.length === 0) return; // nothing to highlight

  const markInstance = new Mark(element);
  markInstance.mark(matches, {
    iframesTimeout: 2000,
    caseSensitive: true,
    separateWordSearch: false,
    diacritics: false,
  });
};

function initialize_regex_table(column_name, column_data, match, match_option) {
  // Find the context div
  const contextDiv = document.querySelector(".context");
  if (!contextDiv) return;

  // Clean context except header
  Array.from(contextDiv.children).forEach((child) => {
    if (!child.classList.contains("header")) {
      contextDiv.removeChild(child);
    }
  });

  // Set header text
  const headerDiv = contextDiv.querySelector(".header");
  if (headerDiv) {
    headerDiv.textContent = column_name;
  }

  // Add items and highlight individually
  if (Array.isArray(column_data)) {
    column_data.forEach((str, index) => {
      const itemDiv = document.createElement("div");
      itemDiv.className = "item";
      itemDiv.textContent = str;
      contextDiv.appendChild(itemDiv);

      // Highlight only this row with its corresponding match
      if (Array.isArray(match) && match[index]) {
        highlight(itemDiv, match[index]);
      }
    });
  }
  // Clean extra highlighted items if  first_occurence = 0 //

  if (match_option == 0) {
    document.querySelectorAll(".item").forEach((item) => {
      const marks = item.querySelectorAll("mark");

      if (marks.length > 1) {
        // Keep the first <mark> as is
        marks.forEach((mark, index) => {
          if (index > 0) {
            // Replace other <mark> tags with their text content
            const textNode = document.createTextNode(mark.textContent);
            mark.replaceWith(textNode);
          }
        });
      }
    });
  }
}
