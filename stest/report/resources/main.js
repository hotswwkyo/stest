/*
 ** filename        main.js
 ** description     html test report javascript
 ** version         1.0.0
 ** author          siwenwei
 */
var seven = window.seven || {};
seven.dot = ".";

seven.comma = ",";

seven.space = " ";

seven.author = "siwenwei";

seven.iconfont = "seveniconfont";

seven.isString = function (obj) {

	return $.type(obj) === 'string';
};

seven.isNumber = function (obj) {
	var patrn = /^(-)?\d+(\.\d+)?$/;
	return patrn.test(obj);
};

seven.isInteger = function (obj) {

	return ($.type(obj) === "number") && (obj % 1 === 0);
};

seven.isArray = function (obj) {

	return $.isArray(obj);
};

seven.isFunction = function (obj) {
	return $.isFunction(obj);
};

seven.isEmptyObject = function (obj) {
	return $.isEmptyObject(obj);
}

seven.isJqueryObject = function (obj) {
	return (obj instanceof $);
};

seven.argumentsToArray = function (js_arguments) {
	var args = [];
	for (var i = 0; i < js_arguments.length; i++) {
		args.push(js_arguments[i]);
	}
	return args;
};

seven.createIcon = function (klass) {
	var jq_icon = $("<i></i>");
	jq_icon.addClass(seven.iconfont);
	if (seven.isArray(klass)) {
		for (var clazz in klass) {
			if (seven.isString(clazz) && clazz) {
				jq_icon.addClass(clazz);
			}
		}
	} else if (seven.isString(klass) && klass) {
		jq_icon.addClass(klass);
	} else {
		var todo = "nothing to do!";
	}
	return jq_icon;
};
seven.fieldset = function (settings) {

	this.dot = seven.dot;
	this.space = seven.space;
	this.klass = "seven-fieldset";
	this.itemKlass = "seven-fieldset-item";
	this.titleKlass = "seven-fieldset-title";
	this.contentKlass = "seven-fieldset-content";
	this.iconKlass = {
		show: "",
		hidden: "",
	};
	this.defaultHiddenCSS = "seven-fieldset-item-hidden";
	var icon_key = "icon";
	if (settings !== undefined && $.isPlainObject(settings) && settings.hasOwnProperty(icon_key)) {
		var icon = settings[icon_key];
		if ($.isPlainObject(icon)) {
			if (icon.hasOwnProperty("show")) {
				this.iconKlass.show = icon.show;
			}
			if (icon.hasOwnProperty("hidden")) {
				this.iconKlass.show = icon.hidden;
			}
		} else if (seven.isString(icon)) {
			this.iconKlass.show = icon;
			this.iconKlass.hidden = icon;
		}
	}
};

seven.fieldset.prototype.init = function (fieldsetFilter, afterHandlers) {

	var fieldsetSelector = this.dot + this.klass;
	var itemSelector = this.dot + this.itemKlass;
	var titleSelector = this.dot + this.titleKlass;
	var contentSelector = this.dot + this.contentKlass;

	this.itemSelector = itemSelector
	this.titleSelector = titleSelector
	this.contentSelector = contentSelector

	this.jq_fieldsets = $(fieldsetSelector);
	if (arguments.length > 0 && typeof fieldsetFilter !== 'undefined') {
		this.jq_fieldsets = this.jq_fieldsets.filter(fieldsetFilter);
	}

	this.jq_items = this.jq_fieldsets.children(itemSelector);
	this.jq_titles = this.jq_items.children(titleSelector);
	this.jq_contents = this.jq_items.children(contentSelector);

	this.addIcon();
	this.toggle("click");
	this.defaultHidden();
	if ($.isFunction(afterHandlers)) {
		afterHandlers.call(this);
	}
};

seven.fieldset.prototype.defaultHidden = function (e) {
	var t = this;
	var n = seven.dot + this.klass;
	var s = seven.dot + this.itemKlass;
	var i = seven.dot + this.titleKlass;
	var r = seven.dot + this.contentKlass;
	var a = this.defaultHiddenCSS;
	var o = null;
	if (typeof e !== undefined && seven.isJqueryObject(e)) {
		o = e
	} else {
		var l = $(n);
		o = l.children(s).filter(seven.dot + a)
	}
	o.each(function () {
		var e = $(this).children(i).children(seven.dot + seven.iconfont).first().filter(function () {
			var e = $(this);
			return e.hasClass(t.iconKlass.show) || e.hasClass(t.iconKlass.hidden)
		});
		e.removeClass(t.iconKlass.show).addClass(t.iconKlass.hidden);
		$(this).children(r).hide()
	})
};

seven.fieldset.prototype.buildSelf = function () {

	var jq_fieldset = $("<div></div>");
	jq_fieldset.addClass(this.klass);
	return jq_fieldset;
};

seven.fieldset.prototype.buildItem = function () {

	var jq_item = $("<div></div>");
	var jq_title = $("<div></div>");
	var jq_content = $("<div></div>");

	jq_item.addClass(this.itemKlass);
	jq_title.addClass(this.titleKlass);
	jq_content.addClass(this.contentKlass);
	jq_item.append(jq_title);
	jq_item.append(jq_content);
	return {
		item: jq_item,
		title: jq_title,
		content: jq_content
	};
};

/** 设置了图标字体class 才会添加图标元素, 否则不会添加
 ***	@param jqTitle title元素
 ***
 */
seven.fieldset.prototype.addIcon = function (jqTitle, titleFilter) {

	var self = this;
	if (self.iconKlass.show && !self.iconKlass.hidden) {
		self.iconKlass.hidden = self.iconKlass.show;
	} else if (!self.iconKlass.show && self.iconKlass.hidden) {
		self.iconKlass.show = self.iconKlass.hidden;
	}

	if (!(self.iconKlass.show && self.iconKlass.hidden)) {
		return;
	}
	var attach_jq_title = self.jq_titles;
	if (arguments.length == 1) {
		attach_jq_title = jqTitle;
	} else if (arguments.length >= 2) {
		attach_jq_title = jqTitle.filter(titleFilter);
	}
	attach_jq_title.filter(function () {
		var jq_el = $(this).children().first();
		if (jq_el.hasClass(self.iconKlass.show) || jq_el.hasClass(self.iconKlass.hidden)) {
			return false;
		} else {
			return true;
		}
	}).prepend(seven.createIcon(this.iconKlass.hidden));
};

/**
 ** 绑定事件到标题或者其子元素用以显示或隐藏标题的同级内容区域
 ** @param events		同jquery 的on方法参数events
 ** @param options 		type:PlainObject A map of additional options to pass to the method.
 **			jq_titles 		:  要绑定标题元素
 **			childSelector	: 标题元素子选择器字符串或者方法(将传递一个标题元素给该方法，需要该方法返回标题的子元素)，绑定到指定的子元素，如果省略则绑定事件到标题元素
 **			notifier		: 当执行翻转内容时，会调用该方法并传递一个状态参数，告知将要翻转到的状态 show - 表示将显示内容  hidden - 表示将隐藏内容，this将指向被翻转内容的同级标题元素jq_title
 ** @see toggle_sibling_content_of_title(events, jq_titles, childSelector, notifier)
 */
seven.fieldset.prototype.toggle = function (events, options) {

	var self = this;
	var jq_titles_key = "jq_titles";
	var child_selector_Key = "childSelector";
	var notifier_key = "notifier";

	var jq_titles = self.jq_titles;
	var childSelector = null;
	var notifier = null;

	if (options !== undefined && $.isPlainObject(options)) {

		var jq_titles_val = options[jq_titles_key];
		var childSelector_val = options[child_selector_Key];
		var notifier_val = options[notifier_key];

		if (jq_titles_val !== undefined && seven.isJqueryObject(jq_titles_val)) {
			jq_titles = jq_titles_val;
		}

		if (childSelector_val !== undefined && (seven.isString(childSelector_val) || seven.isFunction(childSelector_val))) {
			childSelector = childSelector_val;
		}

		if (notifier_val !== undefined && seven.isFunction(notifier_val)) {
			notifier = notifier_val;
		}
	}
	this.toggle_sibling_content_of_title(events, jq_titles, childSelector, notifier);
};

/**
 ** 绑定事件到标题或者其子元素用以显示或隐藏标题的同级内容区域
 ** @param events 			同jquery 的on方法参数events
 ** @param jq_titles			要绑定标题元素
 ** @param childSelector 	标题元素子选择器字符串或者方法(将传递一个标题元素给该方法，需要该方法返回标题的子元素)，绑定到指定的子元素，如果省略则绑定事件到标题元素
 ** @param notifier 			当执行翻转内容时，会调用该方法并传递一个状态参数，告知将要翻转到的状态 show - 表示将显示内容  hidden - 表示将隐藏内容，this将指向被翻转内容的同级标题元素jq_title
 **
 */
seven.fieldset.prototype.toggle_sibling_content_of_title = function (events, jq_titles, childSelector, notifier) {

	var self = this;
	var sibling_title_of_content = this.jq_titles;
	if (jq_titles !== undefined && seven.isJqueryObject(jq_titles)) {
		sibling_title_of_content = jq_titles;
	}

	sibling_title_of_content.each(function () {

		var jq_title = $(this);
		var jq_icon = jq_title.children(seven.dot + seven.iconfont).first().filter(function () {
			var jq_el = $(this);
			return jq_el.hasClass(self.iconKlass.show) || jq_el.hasClass(self.iconKlass.hidden);
		});
		var fn = function (event) {
			var jq_conent = jq_title.next(self.contentSelector);
			if (jq_conent.is(":hidden")) {
				jq_icon.removeClass(self.iconKlass.hidden).addClass(self.iconKlass.show);
				if (notifier !== undefined && $.isFunction(notifier)) {
					notifier.call(jq_title, "show");
				}
				jq_conent.slideDown("slow");
			} else {
				jq_icon.removeClass(self.iconKlass.show).addClass(self.iconKlass.hidden);
				if (notifier !== undefined && $.isFunction(notifier)) {
					notifier.call(jq_title, "hidden");
				}
				jq_conent.slideUp("slow");
			}
		};

		if (childSelector !== undefined) {
			if (seven.isString(childSelector) && (jq_title.find(childSelector).length > 0)) {
				jq_title.off(events).on(events, childSelector, fn);
			} else if ($.isFunction(childSelector)) {
				jq_title.off(events);
				childSelector(jq_title).off(events).on(events, null, fn);
			} else {
				jq_title.off(events).on(events, null, fn);
			}
		} else {
			jq_title.off(events).on(events, null, fn);
		}
	});
};

function argumentsToArray(js_arguments) {
	var args = [];
	for (var i = 0; i < js_arguments.length; i++) {
		args.push(js_arguments[i]);
	}
	return args;
}

function joinWithDot() {
	var dot = ".";
	return argumentsToArray(arguments).join(dot);
}

function isInArray(array, val) {
	var isIn = false;
	for (var i = 0; i < class_name_list.length; i++) {
		if (class_name_list[i] == val) {
			isIn = true;
			break;
		}
	}
}

function addClass() {

	var blank_space = " ";
	var position = null;
	if (arguments.length < 2) {
		return;
	} else if (arguments.length < 3) {
		position = null;
	} else {
		position = arguments[2];
	}
	var element = arguments[0];
	var className = arguments[1];
	var class_name_list = element.className.split(blank_space);
	var is_contains = false;

	for (var i = 0; i < class_name_list.length; i++) {
		if (className == class_name_list[i]) {
			is_contains = true;
			break;
		}
	}

	if (!is_contains) {
		if (position != null && position <= class_name_list.length) {
			class_name_list.splice(position, 0, className);
		} else {
			class_name_list.push(className)
		}
	}

	element.className = class_name_list.join(blank_space); //element.className =
}

function removeClass(element, css_class_name) {

	var blank_space = " ";
	var old_css_classes = element.className.split(blank_space);
	for (var i = 0; i < old_css_classes.length; i++) {
		if (css_class_name == old_css_classes[i]) {
			old_css_classes.splice(i, 1);
		}
	}

	element.className = old_css_classes.join(blank_space)
}

function toggleTestCaseOfTestPoint(testpoint_id, testcase_prefix, id_sep, testcase_count) {

	var hidden = "none";
	var show = "table-row";

	var show_css_class = "testcase-show"
	var hidden_css_class = "testcase-hidden"

	for (var i = 0; i < testcase_count; i++) {
		tc_id = testpoint_id + id_sep + testcase_prefix + (i + 1)
		el_tc_row = document.getElementById(tc_id)
		style = window.getComputedStyle(el_tc_row);
		display = style.display == hidden ? show : hidden;
		el_tc_row.style.display = display
		if (display != show) {
			document.getElementById(tc_id + id_sep + "teststeps").style.display = display
			removeClass(el_tc_row, show_css_class)
			addClass(el_tc_row, hidden_css_class)
		} else {
			removeClass(el_tc_row, hidden_css_class)
			addClass(el_tc_row, show_css_class)
		}
	}
}

function toggleTestStepsRow(teststep_row_id) {

	var hidden = "none";
	var show = "table-row";
	var ts_container_row = document.getElementById(teststep_row_id);
	var ts_c_row_style = window.getComputedStyle(ts_container_row);

	display = ts_c_row_style.display == hidden ? show : hidden;
	ts_container_row.style.display = display
}

function toggleTestStepsDetails(teststep_details_row_id) {

	var hidden = "none";
	var show = "table-row";
	var ts_container_row = document.getElementById(teststep_details_row_id);
	var ts_c_row_style = window.getComputedStyle(ts_container_row);

	display = ts_c_row_style.display == hidden ? show : hidden;
	ts_container_row.style.display = display
}

function show_image_on_new_window(el_img) {
	var w = window.open();
	var img = w.document.createElement('img');
	img.src = el_img.src;
	w.document.body.innerHTML = img.outerHTML;
	w.document.body.ondblclick = function () {
		w.close()
	};
}

$(document).ready(function () {

	fs_args = new seven.fieldset({
		icon: "seven-icon-var-circle"
	});
	fs_args.init(function () {
		return ($(this).children(fs_args.itemSelector).children(fs_args.titleSelector).children('.seven-testcase-args').length > 0);
	});
	fs_kwargs = new seven.fieldset({
		icon: "seven-icon-var-circle"
	});
	fs_kwargs.init(function () {
		return ($(this).children(fs_args.itemSelector).children(fs_args.titleSelector).children('.seven-testcase-kwargs').length > 0);
	});
	fs_traceback = new seven.fieldset({
		icon: "seven-icon-var"
	});
	fs_traceback.init(function () {
		return ($(this).children(fs_args.itemSelector).children(fs_args.titleSelector).children('.seven-testcase-traceback').length > 0);
	});
	fs_extra_info = new seven.fieldset({
		icon: "seven-icon-tips"
	});
	fs_extra_info.init(function () {
		return ($(this).children(fs_args.itemSelector).children(fs_args.titleSelector).children('.seven-testcase-extra-info').length > 0);
	});
	fs_screenshot = new seven.fieldset({
		icon: "seven-icon-step"
	});
	fs_screenshot.init(function () {
		return ($(this).children(fs_args.itemSelector).children(fs_args.titleSelector).children('.seven-testcase-screenshots').length > 0);
	});
});
