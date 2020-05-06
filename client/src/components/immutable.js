export default class Immutable {
	static updateObjectInArray(array, keyName, keyValue, fieldName, fieldValue) {
		return array.map((x) => {
			if (x[keyName] === keyValue) {
				return {
					...x,
					[fieldName]: fieldValue
				};
			}
			return x
		});
	}
	static setSelectedObjectInArray(array, keyName, keyValue, nextNumber) {
		const arr = array.map((x) => {
			if (x[keyName] === keyValue) {
				const newSelectedValue = (x.selected > -1) ? -1 : nextNumber
				if (newSelectedValue > -1 && nextNumber === 5) return x;
				return {
					...x,
					selected: newSelectedValue
				};
			}
			return x
		});
		let c = -1;
		return arr.map((x) => {
			if (x.selected > -1) {
				c++;
				return {
					...x,
					selected: c
				};
			}
			return x
		});
	}

}
