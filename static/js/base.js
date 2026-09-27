/** /static/base.js javascript functionality for a browser window */

/** pageOnLoad() javascript function for loading unobtrusive javascript event listeners into the browser window.
 *
 * loads scripts so that actions such as clicking on an element with the appropriate class given to it:
 *     - clicking element with class expandCollapse will
 * @example
 * <script>window.onload = pageOnLoad; // </script>
 *
 * @todo Review base.js code for overlap with bootstrap5
 */
function pageOnLoad() {
  // This function sets all of the event listeners for the elements on the web page
  // There should normally be only one window on load event handler, so combining of them may be necessary
  // event listeners are set here, attaching functions defined below

  /** onclick event on .expandCollapse to alternately expand or collapse the block*/
  document.querySelectorAll(".expandCollapse").forEach(
    el => {
      console.log("element with the expandCollapse class: ".concat(el.tagName))
      // el should be an article element, where the expandCollapse class was added
      const children = el.children;
      const head = el.querySelector("header");
      if (head !== null) {
        console.log("header for the expandCollapse class: ".concat(head.tagName))
        head.addEventListener("click", (event) => expanderCollapser(event))
      } else {
        console.log("header is missing under expandCollapse class")
      }
      // el.addEventListener("click", (event) => expanderCollapser(event))
    }
  )

  /** onclick event on all a tags, to prevent page reloads a tags with target _blank*/
  document.querySelectorAll("a").forEach(
    el => el.addEventListener("click", (event) => blankATags(event))
  )
}


/*********************************************************************************************************************
 * support functions for pageOnLoad function
 **********************************************************************************************************************/


/*********************************************************************************************************************
 * expanderCollapser() javascript function for the functionality of .expandCollapse in pageOnLoad() function
 * @param {Event} event - browser event listener
 */
// expands or collapses the section of an article when the header is clicked
function expanderCollapser(event) {
  // console.log("Clicked a header element with an article with the expandCollapse class")
  const elem = event.currentTarget;
  // console.log("called expanderCollapser on element with with tag: ".concat(elem.tagName));
  const parent = elem.parentElement;
  // console.log("parent with expanderCollapser on element with with tag: ".concat(parent.tagName));
  // console.log("ARTICLE element classList: ".concat(parent.classList));
  const wasExpanded = parent.classList.contains("expanded");
  // console.log("parent element was element initially expanded: ".concat(wasExpanded.toString()));

  if (wasExpanded === true) {
    parent.classList.remove("expanded");
  } else {
    parent.classList.add("expanded");
  }
};


/*********************************************************************************************************************
 * JavaScript function for preventing clicks on blanks a tags in pageOnLoad()
 * @param {Event} event - browser event listener
 */
// prevent page refresh when clicking on an a tag with a _blank target
function blankATags(event) {
  // console.log("Clicked an element with the a tag")
  const elem = event.currentTarget;
  // console.log("called blankATags on element with with tag: ".concat(elem.tagName));
  const href = (elem.hasAttribute("href") === true) ? elem.getAttribute("href") : "";
  // console.log("href: ".concat(href.toString()));
  const blankTarget = elem.hasAttribute("target") && elem.getAttribute("target") === "_blank";
  // console.log("blankTarget: ".concat(blankTarget.toString()));
  if (blankTarget === true && href !== "" && href !== "#") {
    // console.log("open window for: ".concat(href.toString()));
    window.open(href)
    event.preventDefault();
    event.stopPropagation();
    }
};



/* *************************************************************************************
 * (global) constants
 */

  // const MY_CONSTANT = "some-value";

  /* *************************************************************************************
  helper methods
  */

  function setErrorMsg(errMsg) {
    errElem = getById("errorMessage");
    if (errElem === null) {
      errElem.textContent=errMsg;
      console.log(errMsg);
    } else {
      console.log("ERROR: Unable to access element with ID: 'errorMessage'");
      console.log("ERROR: Unable to display error message: " + errMsg);
    }
  }

  /* *************************************************************************************
  called functions
  */

  function setFontSize(fontSize) {
    htmlElems = document.getElementsByTagName("html");
    if (htmlElems.length == 1) {
      htmlElems[0].style.fontSize = fontSize;
    } else {
      setErrorMsg("ERROR: unable to find the 'html' element!");
    }
  }

  function isMobileDevice() {
    /android|iphone|kindle|ipad/i.test(navigator.userAgent)
  }
