/**
 * jQuery UI init for the landing page demo (Story 1-1).
 * Expects jQuery, jQuery UI, and #welcome-accordion in the DOM.
 */
(function ($) {
  "use strict";
  $(function () {
    var $acc = $("#welcome-accordion");
    if ($acc.length) {
      $acc.accordion({ collapsible: true, active: false, heightStyle: "content" });
    }
  });
})(jQuery);
