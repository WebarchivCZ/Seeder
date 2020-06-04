// ----------------------------------------------------------------------------
// Text manipulation
// ----------------------------------------------------------------------------
// Source: https://stackoverflow.com/questions/985272/selecting-text-in-an-element-akin-to-highlighting-with-your-mouse/987376#987376
function selectText(node) {
  if (document.body.createTextRange) {
      const range = document.body.createTextRange();
      range.moveToElementText(node);
      range.select();
  } else if (window.getSelection) {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(node);
      selection.removeAllRanges();
      selection.addRange(range);
  } else {
      console.warn("Could not select text in node: Unsupported browser.");
  }
}