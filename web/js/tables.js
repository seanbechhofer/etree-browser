// javascript for manipulating exam results and tables. 
function showAllStudents() {
  tds = document.getElementsByTagName("td");
  for (var i=0; i<tds.length; i++) {showElement(tds[i])};

  ths = document.getElementsByTagName("th");
  for (var i=0; i<ths.length; i++) {showElement(ths[i])};

  studs = document.getElementsByClassName("student");
  for (var i=0; i<studs.length; i++) {showElement(studs[i])};
}

function hideAllStudents() {
  studs = document.getElementsByClassName("student");
  for (var i=0; i<studs.length; i++) {hideElement(studs[i])};
}

function showElement(el) {
  el.style.display = "";
}

function hideElement(el) {
  el.style.display = "none";
}

function hideElementId(id) {
  hideElement(document.getElementById(id))
}

function hideElements(cl) {
  els = document.getElementsByClassName(cl);
  for (var i=0; i<els.length; i++) {hideElement(els[i])};
}

function showElements(cl) {
  els = document.getElementsByClassName(cl);
  for (var i=0; i<els.length; i++) {showElement(els[i])};
}

function showStudents(cl) {
  hideAllStudents();
  showElements(cl);
}

