export const courses = [
  { id:'agp-301', code:'AGP 301', title:'Geophysical Methods', level:'300 Level', category:'Geophysics', description:'Foundations of gravity, magnetic, electrical and seismic methods used in subsurface investigation.', progress:72, averageScore:84, questions:42, topics:4, color:'purple' },
  { id:'geo-305', code:'GEO 305', title:'Structural Geology', level:'300 Level', category:'Geology', description:'Study of rock deformation, geological structures, stress, strain and tectonic interpretation.', progress:48, averageScore:78, questions:36, topics:5, color:'gold' },
  { id:'pet-301', code:'PET 301', title:'Petrology', level:'300 Level', category:'Petrology', description:'Mineral assemblages, igneous and metamorphic processes, textures and rock classification.', progress:31, averageScore:81, questions:30, topics:4, color:'magenta' },
  { id:'sed-302', code:'SED 302', title:'Sedimentology', level:'300 Level', category:'Sedimentology', description:'Sediment transport, depositional environments, sedimentary structures and facies.', progress:18, averageScore:75, questions:28, topics:4, color:'blue' },
  { id:'min-304', code:'MIN 304', title:'Mineralogy', level:'300 Level', category:'Mineralogy', description:'Crystal chemistry, mineral identification, optical properties and mineral systems.', progress:9, averageScore:72, questions:25, topics:3, color:'green' },
  { id:'seis-402', code:'GEO 402', title:'Seismology', level:'400 Level', category:'Geophysics', description:'Seismic waves, earthquake sources, travel-time analysis and Earth structure.', progress:0, averageScore:0, questions:32, topics:4, color:'purple' },
];
export const getCourse = id => courses.find(c => c.id === id);
