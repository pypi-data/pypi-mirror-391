from subcutaneous import container


@container
class Trace_Methods:
	def getSuffix(idx):
		axis_idx = ""
		if idx == 0:
			return axis_idx
		return str(idx + 1)

	def getTraceIndex(row, col, n_cols):
		return (row - 1) * n_cols + (col - 1)

	def expand_y(fig, idx):
		suffix = Trace_Methods.getSuffix(idx)
		x_domain = fig.layout[f"xaxis{suffix}"]["domain"]

		diff = x_domain[1] - x_domain[0]
		new_dom = (x_domain[0], x_domain[1] + diff)
		fig._layout[f"xaxis{suffix}"].update({"domain": new_dom})
		return fig

	def inverseTraceIndex(index, n_cols):
		_row = index // n_cols	# [NOTE] actual row is _row +1
		_col = index % n_cols	# [NOTE] actual col is _col +1
		return _row, _col

	def updateFigure(fig, trace, idx, *args, expand_col=False, **kwargs):
		suffix = Trace_Methods.getSuffix(idx)

		if "z" in trace:
			trace._orphan_props["scene"] = f"scene{suffix}"

			if fig._grid_ref:

				try:
					n_cols = len(fig._grid_ref[0])
					row, col = Trace_Methods.inverseTraceIndex(idx, n_cols)
					if not fig._grid_ref[row][col][0].subplot_type == "scene":
						# [NOTE] using NotImplementedError as a low probability of intercept raise
						raise NotImplementedError

				except NotImplementedError as e:

					y_domain = fig.layout[f"yaxis{suffix}"]["domain"]
					x_domain = fig.layout[f"xaxis{suffix}"]["domain"]

					scene = {
						"domain": {"x": x_domain, "y": y_domain, "column": col + 1, "row": row + 1}
					}

					# fig._layout[f"scene{suffix}"] = scene
					fig._layout.update(({f"scene{suffix}": scene}))

					# [NOTE]  The figure attributes `yaxis{suffix}` and `xaxis{suffix}` don't need to be kept to preserve indexing
					# fig.layout.pop(f"yaxis{suffix}", None)
					# fig.layout.pop(f"xaxis{suffix}", None)

		fig._data[idx] = trace._orphan_props
		for k, v in trace._orphan_props.items():
			try:
				fig._data[idx][k] = v	# trace._orphan_props
				fig.data[idx][k] = v	# trace._orphan_props

			except:
				pass
		return fig

	def formatOrphan(orphan, idx):
		suffix = Trace_Methods.getSuffix(idx)
		orphan_update = dict()

		if "z" in orphan:
			orphan_update.update({"scene": f"scene{suffix}"})
		else:

			orphan_update = {"xaxis": f"x{suffix}", "yaxis": f"y{suffix}"}

		orphan._orphan_props.update(orphan_update)
		return orphan

	def appendData(fig, data, idx, *args, **kwargs):

		for k, v in data.items():
			if k.endswith("axis"):
				fig._data[idx][k] = v	# [NOTE] Manipulate `_data` so propagated to widgets too
			elif k != "uid":
				if k in ["x", "y", "z"]:

					_data = getattr(fig.data[idx], k, [])
					if _data is None:
						_data = []
					_data = list(_data)

					_data.extend(v)
					fig._data[idx][k] = _data
			else:

				fig._data[idx][k] = v
				fig.data[idx][k] = v

		return fig

	def addTrace(fig, trace, idx, *args, _modification_type="append", **kwargs):
		suffix = Trace_Methods.getSuffix(idx)

		target_trace = fig.data[idx]
		if target_trace.type != trace.type:
			fig = Trace_Methods.updateFigure(fig, trace, idx, *args, **kwargs)
		else:
			data = {"x": trace.x, "y": trace.y}
			if "z" in trace:
				data["z"] = trace["z"]
			data.update({"xaxis": f"x{suffix}", "yaxis": f"y{suffix}"})

			if "uid" in trace:

				data["uid"] = trace["uid"]

			for k, v in dict(vars(trace)).items():
				if k not in data:
					data[k] = v
			if _modification_type == "append":

				fig = Trace_Methods.appendData(fig, data, idx, *args, **kwargs)

		return fig
