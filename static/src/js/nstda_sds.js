openerp.nstda_sds = function(instance) {

	var MODELS_TO_HIDE = ['nstda.sds.googleapis'];

	var QWeb = instance.web.qweb, _t = instance.web._t, _lt = instance.web._lt;
	var dateBefore = null;
	var get_status = {};

	instance.web.ListView.include({
		load_list : function() {
            var self = this;
            var ret = this._super.apply(this, arguments);
            var res_model = this.dataset.model;
            if ($.inArray(res_model, MODELS_TO_HIDE) != -1) {
            	self.options.importable = false;
            	$(".oe_fade, .oe_list_button_import, .oe_list_add").remove();
            };
            return ret;	
		},
	});

}