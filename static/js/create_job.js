$('document').ready(function () {
	const sameday = {
		price : 4.00,
		minutes: 240,
		label : 'Same Day',
	}
	const regular = {
		price : 7.00,
		minutes: 120,
		label : 'Regular',
	}
	const rush = {
		price : 13.00,
		minutes: 60,
		label : 'Rush',
	}
	const double_rush = {
		price : 18.00,
		minutes: 30,
		label : 'Double Rush',
	}

	const SERVICE_DICT = {
		sameday,
		regular,
		rush,
		double_rush,
	}

	function update() {
		let value = $('#id_service').val();
		if (value != 'None'){
			let {minutes, price, label} = SERVICE_DICT[value];
			$('#id_minutes_due_after_start').val(minutes);
			$('#id_points').val(price);
			$('#id_service_label').val(label);
		}

	}

	$('#id_service').change(function() {
		update();
	});

});
