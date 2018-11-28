odoo.define('login_form.form_widgets', function(require) {
  "use strict";
  var web = require('web.AbstractWebClient');
  var utils = require('web.utils');
  var Widget = require('web.Widget');
  web.include({
        init: function(parent) {
            this.client_options = {};
            this._super(parent);
            this.origin = undefined;
            this._current_state = null;
            this.menu_dm = new utils.DropMisordered();
            this.action_mutex = new utils.Mutex();
            this.set('title_part', {"zopenerp": "Promtest"});
        }
  });
});