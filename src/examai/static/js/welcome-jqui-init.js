/**
 * jQuery UI accordion init (Story 1-1 demo assets). Expects jQuery, jQuery UI, and #welcome-accordion.
 * Not loaded by `/` after Story 8-9; kept for optional demos and static route tests.
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
