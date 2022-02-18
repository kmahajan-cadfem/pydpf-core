from ansys.dpf import core as dpf
from ansys.dpf.core import examples
from ansys.dpf.core.plotter import DpfPlotter

model = dpf.Model(examples.simple_bar)
print(model)
metadata = model.metadata
results = model.results
displacements = results.displacement()
fields = displacements.outputs.fields_container()

# Finally, extract the data of the displacement field:
disp = fields[0].data

# Get norm
norm = dpf.operators.math.norm(field=fields[0])
norm_disp = norm.outputs.field.get_data()

ux = disp[:, 0]
uy = disp[:, 1]
uz = disp[:, 2]

# UX
comp_sel_x = dpf.operators.logic.component_selector(field=fields[0], component_number=0)
ux_field = comp_sel_x.outputs.field.get_data()

# UX
comp_sel_y = dpf.operators.logic.component_selector(field=fields[0], component_number=1)
uy_field = comp_sel_y.outputs.field.get_data()

# UX
comp_sel_z = dpf.operators.logic.component_selector(field=fields[0], component_number=2)
uz_field = comp_sel_z.outputs.field.get_data()

plot = DpfPlotter()
plot.add_field(fields[0], opacity=0.5, show_vectors=True, vector_scale=1e4)
plot.show_figure(show_axes=True)
