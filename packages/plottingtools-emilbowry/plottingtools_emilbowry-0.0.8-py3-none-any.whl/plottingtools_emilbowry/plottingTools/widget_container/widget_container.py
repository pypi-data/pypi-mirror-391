import ipywidgets as widgets


class WidgetContainer:
	def meta(self, *args, **kwds):
		return type(*args, **kwds)

	def tagged(self, *args, _id, **kwds):
		my_id = _id
		owner = self

		class tagged(metaclass=owner.meta):
			identifier = my_id

			def __new__(cls, *args, **kwds):
				instance = object.__new__(cls)
				return instance

			def __init__(self, _function):
				self.func = _function
				owner.updateFunctions.append(self.func)

			def __call__(self, *args, **kwargs):
				self.func(*args, **kwargs)
				owner.computeAux(my_id, *args, **kwargs)

		return tagged


class gridSliderContainer(WidgetContainer):
	@staticmethod
	def _idx(val, data):
		return int(round((val - data[0]) / (data[1] - data[0])))

	@staticmethod
	def _closedIdx(data):
		def _inner(val):
			return gridSliderContainer._idx(val, data)

		return _inner

	@staticmethod
	def createSlider(*, value, _min, _max, step, description, continuous_update, **kwargs):
		slider = widgets.FloatSlider(
			value=value,
			min=_min,
			max=_max,
			step=step,
			description=description,
			continuous_update=continuous_update,
		)

		return slider

	def _createSlider(self, _slider_dict, **kwargs):
		slider_name = list(_slider_dict.keys())[0]
		slider_dict = list(_slider_dict.values())[0]
		slider_data = slider_dict["data"]
		creation_dict = dict(
			value=float(slider_data[0]),
			_min=float(slider_data.min()),
			_max=float(slider_data.max()),
			step=float(slider_data[1] - slider_data[0]),
			description=f"{slider_name}",
			continuous_update=slider_dict.get("continuous_update", False),
		)
		creation_dict.update(**kwargs)

		slider = gridSliderContainer.createSlider(**creation_dict)

		self.Sliders[slider_name] = slider
		self.Slider_idxFn[slider_name] = gridSliderContainer._closedIdx(slider_data)
		self.Sliders[slider_name].observe(self.refresh, names="value")

	@property
	def sliders(self):
		return list(self.Sliders.values())

	def __init__(self, slider_dicts, update_functions, data, **kwargs):

		self.Sliders = dict()
		self.Slider_idxFn = dict()
		self.auxilliary = dict()

		for i in slider_dicts:
			self._createSlider(i)
		for k, v in kwargs.items():
			setattr(self, k, v)
		self.updateFunctions = update_functions	# list probably
		self.data = data

	def _refreshSliders(self, *args, **kwargs):
		slider_indices = dict()
		Slider_Values = dict()
		for k, v in self.Sliders.items():
			value = v.value
			slider_indices[k] = self.Slider_idxFn[k](value)
			Slider_Values[k] = value
		return slider_indices, Slider_Values

	def _updateFigure(self, slider_indices, values, *args, **kwargs):

		for fn in self.updateFunctions:
			fn(
				fig=self.fig,
				data=self.data,
				slider_indices=slider_indices,
				values=values,
				*args,
				**kwargs,
			)

	def refresh(self, *args, **kwargs):
		slider_indices, Slider_Values = self._refreshSliders(*args, **kwargs)
		with self.fig.batch_update():
			self._updateFigure(slider_indices, Slider_Values)

	def __call__(self, fig):
		self.fig = fig

		for i in fig.data:
			if hasattr(i, "meta") and i.meta is not None:
				if "id" in i.meta:
					self.auxilliary[i.meta["id"]] = {"index": fig.data.index(i)}
				if "axis" in i.meta:
					self.auxilliary[i.meta["id"]]["axis"] = i.meta["axis"]
				if "data_idx" in i.meta:
					self.auxilliary[i.meta["id"]]["data_idx"] = i.meta["data_idx"]
				for k, v in i.meta.items():
					if k not in self.auxilliary[i.meta["id"]]:
						self.auxilliary[i.meta["id"]][k] = v
		self.controls = widgets.VBox(self.sliders)	# , layout=widgets.Layout(width="100%")
		self.container = widgets.VBox([self.controls, self.fig])
		return self

	def computeAux(self, _id, *, data, slider_indices, values, **kwargs):
		aux = self.auxilliary[_id]
		idx = aux["index"]
		_data_idx = aux["data_idx"]
		ax = aux["axis"]
		data_idx = []
		for i in _data_idx:
			if isinstance(i, str):
				if i == "__SLICE__":
					data_idx.append(i)
					data_idx[-1] = slice(None)
				else:
					v = slider_indices[i]
					data_idx.append(v)
			else:
				data_idx.append(i)

		self.fig.data[idx][ax] = data[tuple(data_idx)]
