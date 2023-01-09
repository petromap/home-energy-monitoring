INSERT INTO public.locations(location_id, location_name, sensor_name) VALUES (1, 'kitchen', 'heatpump');
INSERT INTO public.locations(location_id, location_name, sensor_name) VALUES (2, 'garden', 'weather station');
SELECT setval('public.locations_location_id_seq', (select count(*)+1 from public.locations), true);

INSERT INTO public.measurement_types(parameter_id, parameter_name, unit) VALUES (1, 'Electric energy consumption (kWh)', 'kWh');
INSERT INTO public.measurement_types(parameter_id, parameter_name, unit) VALUES (2, 'Electric energy production (kWh)', 'kWh');
INSERT INTO public.measurement_types(parameter_id, parameter_name, unit) VALUES (3, 'Temperature (ºC)', 'ºC');
SELECT setval('public.measurement_types_parameter_id_seq', (select count(*)+1 from public.measurement_types), true);

-- Two values, one measurement per day except simulated repeat and reset
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '7 days', 1, 1, 442.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '6 days', 1, 1, 466.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '5 days' - interval '2 hours', 1, 1, 486.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '5 days' - interval '1 hours', 1, 1, 486.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '5 days', 1, 1, 486.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '4 days', 1, 1, 502.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '3 days', 1, 1, 517.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '2 days', 1, 1, 26.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '1 days', 1, 1, 40.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now(), 1, 1, 78.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '7 days', 2, 1, 1153.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '6 days', 2, 1, 1229.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '5 days' - interval '2 hours', 2, 1, 1293.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '5 days' - interval '1 hours', 2, 1, 1293.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '5 days', 2, 1, 1293.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '4 days', 2, 1, 1347.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '3 days', 2, 1, 1399.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '2 days', 2, 1, 91.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now() - interval '1 days', 2, 1, 119.0);
INSERT INTO public.measurements(measure_time, parameter_id, location_id, v)	VALUES (now(), 2, 1, 225.0);
