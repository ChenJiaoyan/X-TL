import org.semanticweb.HermiT.Reasoner;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.reasoner.NodeSet;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.owlapi.util.DefaultPrefixManager;
import org.semanticweb.owlapi.vocab.OWL2Datatype;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;

class Snapshot {
    private OWLOntologyManager manager = null;
    private OWLDataFactory factory = null;
    private OWLOntology ont = null;
    private OWLDatatype t_int = null;
    private OWLDatatype t_string = null;
    private OWLDatatype t_float = null;
    private String ontIRI = null;
    private PrefixManager pm = null;

    private String HOME_DIR = null;
    private String dom_dir = null;
    private File snp_f = null;

    /**
     * Initialize a snapshot
     *
     * @param dom_name
     * @param snp_name
     * @throws OWLOntologyCreationException
     */
    Snapshot(String snp_dir_name, String dom_name, String snp_name, String home_dir, String iri_s) throws OWLOntologyCreationException {
        manager = OWLManager.createOWLOntologyManager();
        factory = manager.getOWLDataFactory();
        t_int = factory.getOWLDatatype(OWL2Datatype.XSD_INT.getIRI());
        t_string = factory.getOWLDatatype(OWL2Datatype.XSD_STRING.getIRI());
        t_float = factory.getOWLDatatype(OWL2Datatype.XSD_FLOAT.getIRI());
        pm = new DefaultPrefixManager(null, null, iri_s);
        ontIRI = iri_s;

        HOME_DIR = home_dir;
        File d = new File((new File(HOME_DIR, snp_dir_name)).getPath(), dom_name);
        if (!d.exists()) {
            d.mkdir();
        }
        this.dom_dir = d.getPath();
        this.snp_f = new File(dom_dir, snp_name + ".owl");

        loadBootstrapOnto();
    }

    /**
     * add target departure related axioms
     *
     * @param car
     * @param ori
     * @param des
     * @param m
     */
    void addTarget(String car, String ori, String des, HashMap<String, String> m) {
        OWLNamedIndividual I_dep = factory.getOWLNamedIndividual(":dep", pm);
        addClassAssertion("Departure", I_dep);

        OWLNamedIndividual I_car = factory.getOWLNamedIndividual(":car", pm);
        addClassAssertion("Carrier", I_car);
        OWLNamedIndividual I_ori = factory.getOWLNamedIndividual(":ori", pm);
        addClassAssertion("Origin", I_ori);
        OWLNamedIndividual I_des = factory.getOWLNamedIndividual(":des", pm);
        addClassAssertion("Destination", I_des);
        OWLSameIndividualAxiom[] sameIndAxioms = new OWLSameIndividualAxiom[]{
                factory.getOWLSameIndividualAxiom(I_car, factory.getOWLNamedIndividual(":" + car, pm)),
                factory.getOWLSameIndividualAxiom(I_ori, factory.getOWLNamedIndividual(":" + ori, pm)),
                factory.getOWLSameIndividualAxiom(I_des, factory.getOWLNamedIndividual(":" + des, pm)),
        };
        ont.addAxioms(sameIndAxioms);

        addObjectProperty(I_dep, "hasCarrier", I_car);
        addObjectProperty(I_dep, "hasOrigin", I_ori);
        addObjectProperty(I_dep, "hasDest", I_des);

        addDepDataProperties(I_dep, m);
        addDepFlight(I_dep, m);

        addAptCityState(m.get("Origin"), m.get("OriginCityName"));
        addAptCityState(m.get("Dest"), m.get("DestCityName"));
    }

    /**
     * add mete axiom of origin/dest
     *
     * @param ori_or_des
     * @param m
     */
    void addMete(String ori_or_des, HashMap<String, String> m) {
        OWLNamedIndividual I_ori_or_des = factory.getOWLNamedIndividual(":" + ori_or_des, pm);
        OWLNamedIndividual I_wea = factory.getOWLNamedIndividual(String.format(":wea_%s", ori_or_des), pm);
        addClassAssertion("Weather", I_wea);
        addObjectProperty(I_ori_or_des, "hasWeather", I_wea);

        addDataProperty(I_wea, "hasCloudCover", m.get("cloudCover"), t_float);
        addDataProperty(I_wea, "hasDewPoint", m.get("dewPoint"), t_float);
        addDataProperty(I_wea, "hasHumidity", m.get("humidity"), t_float);
        addDataProperty(I_wea, "hasPrecipType", m.get("precipType"), t_string);
        addDataProperty(I_wea, "hasPressure", m.get("pressure"), t_float);
        addDataProperty(I_wea, "hasTemperature", m.get("temperature"), t_float);
        addDataProperty(I_wea, "hasVisibility", m.get("visibility"), t_float);
        addDataProperty(I_wea, "hasWindBearing", m.get("windBearing"), t_float);
        addDataProperty(I_wea, "hasWindSpeed", m.get("windSpeed"), t_float);

        if (m.get("summary") != null) {
            String smy = m.get("summary").trim();
            if (!smy.equals("")) {
                String[] summaries = smy.split("and");
                for (String s : summaries) {
                    addDataProperty(I_wea, "hasSummary", s.trim(), t_string);
                }
            }
        }
    }

    /**
     * add departure axioms of airport
     *
     * @param apt
     * @param deps
     */
    void addAptDep(String apt, ArrayList<HashMap<String, String>> deps) {
        for (int i = 0; i < deps.size(); i++) {
            HashMap<String, String> m = deps.get(i);
            OWLNamedIndividual I_dep = factory.getOWLNamedIndividual(String.format(":dep_%s_r%d", apt, i + 1), pm);
            addClassAssertion("Departure", I_dep);

            OWLNamedIndividual I_car = factory.getOWLNamedIndividual(String.format(":%s", m.get("Carrier")), pm);
            addClassAssertion("Carrier", I_car);
            OWLNamedIndividual I_ori = factory.getOWLNamedIndividual(String.format(":%s", m.get("Origin")), pm);
            addClassAssertion("Airport", I_ori);
            OWLNamedIndividual I_des = factory.getOWLNamedIndividual(String.format(":%s", m.get("Dest")), pm);
            addClassAssertion("Airport", I_des);

            addObjectProperty(I_dep, "hasCarrier", I_car);
            addObjectProperty(I_dep, "hasOrigin", I_ori);
            addObjectProperty(I_dep, "hasDest", I_des);

            addObjectProperty(I_ori, String.format("hasRecDep%d", i + 1), I_dep);

            addDepDataProperties(I_dep, m);
            addDepFlight(I_dep, m);

            addAptCityState(m.get("Origin"), m.get("OriginCityName"));
            addAptCityState(m.get("Dest"), m.get("DestCityName"));
        }
    }


    /**
     * add departure axioms of carrier
     *
     * @param deps
     */
    void addCarDep(ArrayList<HashMap<String, String>> deps) {
        for (int i = 0; i < deps.size(); i++) {
            HashMap<String, String> m = deps.get(i);
            OWLNamedIndividual I_dep = factory.getOWLNamedIndividual(String.format(":dep_car_r%d", i + 1), pm);
            addClassAssertion("Departure", I_dep);

            OWLNamedIndividual I_car = factory.getOWLNamedIndividual(String.format(":%s", m.get("Carrier")), pm);
            addClassAssertion("Carrier", I_car);
            OWLNamedIndividual I_ori = factory.getOWLNamedIndividual(String.format(":%s", m.get("Origin")), pm);
            addClassAssertion("Airport", I_ori);
            OWLNamedIndividual I_des = factory.getOWLNamedIndividual(String.format(":%s", m.get("Dest")), pm);
            addClassAssertion("Airport", I_des);

            addObjectProperty(I_dep, "hasCarrier", I_car);
            addObjectProperty(I_dep, "hasOrigin", I_ori);
            addObjectProperty(I_dep, "hasDest", I_des);

            addObjectProperty(I_car, String.format("hasRecCarDep%d", i + 1), I_dep);

            addDepDataProperties(I_dep, m);
            addDepFlight(I_dep, m);


            addAptCityState(m.get("Origin"), m.get("OriginCityName"));
            addAptCityState(m.get("Dest"), m.get("DestCityName"));
        }
    }


    /**
     * add departure axioms of carrier of origin
     *
     * @param car
     * @param deps
     */
    void addCarOriDep(String car, ArrayList<HashMap<String, String>> deps) {
        for (int i = 0; i < deps.size(); i++) {
            HashMap<String, String> m = deps.get(i);
            OWLNamedIndividual I_dep = factory.getOWLNamedIndividual(String.format(":dep_%s_ori_r%d", car, i + 1), pm);
            addClassAssertion("Departure", I_dep);

            OWLNamedIndividual I_car = factory.getOWLNamedIndividual(String.format(":%s", m.get("Carrier")), pm);
            addClassAssertion("Carrier", I_car);
            OWLNamedIndividual I_ori = factory.getOWLNamedIndividual(String.format(":%s", m.get("Origin")), pm);
            addClassAssertion("Airport", I_ori);
            OWLNamedIndividual I_des = factory.getOWLNamedIndividual(String.format(":%s", m.get("Dest")), pm);
            addClassAssertion("Airport", I_des);

            addObjectProperty(I_dep, "hasCarrier", I_car);
            addObjectProperty(I_dep, "hasOrigin", I_ori);
            addObjectProperty(I_dep, "hasDest", I_des);

            addDepDataProperties(I_dep, m);
            addDepFlight(I_dep, m);

            addObjectProperty(I_car, String.format("hasRecCarOriDep%d", i + 1), I_dep);

            addAptCityState(m.get("Origin"), m.get("OriginCityName"));
            addAptCityState(m.get("Dest"), m.get("DestCityName"));
        }
    }


    void addAptCityState(String aptName, String cityName) {
        if (cityName != null && !cityName.equals("") && cityName.contains(",") && aptName != null && !aptName.equals("")) {
            OWLNamedIndividual I_apt = factory.getOWLNamedIndividual(String.format(":%s", aptName), pm);
            String[] tmp = cityName.trim().split(",");
            String state = tmp[1].trim();
            OWLNamedIndividual I_state = factory.getOWLNamedIndividual(String.format(":S_%s", state), pm);
            addClassAssertion("State", I_state);

            for (String city : tmp[0].trim().split("/")) {
                OWLNamedIndividual I_city = factory.getOWLNamedIndividual(
                        String.format(":%s", city.trim().replace(" ", "_")), pm);
                addClassAssertion("City", I_city);
                addObjectProperty(I_city, "locatedIn", I_state);
                addObjectProperty(I_apt, "serveCity", I_city);
            }
        }
    }

    /**
     * add flight axioms of a departure
     *
     * @param I_dep
     * @param m
     */
    private void addDepFlight(OWLNamedIndividual I_dep, HashMap<String, String> m) {
        OWLNamedIndividual I_flt = factory.getOWLNamedIndividual(String.format(":%s_%s", m.get("Carrier"), m.get("FlightNum")), pm);
        addClassAssertion("Flight", I_flt);
        addObjectProperty(I_dep, "hasFlight", I_flt);
    }

    /**
     * add data properties of a departure
     *
     * @param I_dep
     * @param m
     */
    private void addDepDataProperties(OWLNamedIndividual I_dep, HashMap<String, String> m) {
        addDataProperty(I_dep, "hasCRSDepTime", m.get("CRSDepTime"), t_string);
        addDataProperty(I_dep, "hasDepDelay", m.get("DepDelay"), t_float);
        addDataProperty(I_dep, "hasCRSArrTime", m.get("CRSArrTime"), t_string);
        addDataProperty(I_dep, "hasArrDelay", m.get("ArrDelay"), t_float);
        addDataProperty(I_dep, "hasFlightDate", m.get("FlightDate"), t_string);
        addDataProperty(I_dep, "hasDistance", m.get("Distance"), t_float);
        addDataProperty(I_dep, "hasDistanceGroup", m.get("DistanceGroup"), t_int);
        addDataProperty(I_dep, "hasCarrierDelay", m.get("CarrierDelay"), t_float);
        addDataProperty(I_dep, "hasWeatherDelay", m.get("WeatherDelay"), t_float);
        addDataProperty(I_dep, "hasNASDelay", m.get("NASDelay"), t_float);
        addDataProperty(I_dep, "hasSecurityDelay", m.get("SecurityDelay"), t_float);
        addDataProperty(I_dep, "hasLateAircraftDelay", m.get("LateAircraftDelay"), t_float);
        addDataProperty(I_dep, "hasArrivalDelayGroups", m.get("ArrivalDelayGroups"), t_int);
        addDataProperty(I_dep, "hasDepartureDelayGroups", m.get("DepartureDelayGroups"), t_int);
    }

    /**
     * add a class assertion
     *
     * @param c_name
     * @param i
     */
    private void addClassAssertion(String c_name, OWLNamedIndividual i) {
        ont.addAxiom(factory.getOWLClassAssertionAxiom(factory.getOWLClass(":" + c_name, pm), i));
    }

    /**
     * add an object property
     *
     * @param s
     * @param p_name
     * @param o
     */
    private void addObjectProperty(OWLNamedIndividual s, String p_name, OWLNamedIndividual o) {
        ont.addAxiom(factory.getOWLObjectPropertyAssertionAxiom(
                factory.getOWLObjectProperty(":" + p_name, pm), s, o));
    }

    /**
     * add a data property
     *
     * @param i
     * @param p_name
     * @param v_str
     * @param v_type
     */
    private void addDataProperty(OWLNamedIndividual i, String p_name, String v_str, OWLDatatype v_type) {
        if (v_str != null) {
            v_str = v_str.trim();
            if (!v_str.equals("")) {
                ont.addAxiom(factory.getOWLDataPropertyAssertionAxiom(factory.getOWLDataProperty(
                        ":" + p_name, pm), i, factory.getOWLLiteral(v_str, v_type)));
            }
        }
    }

    /**
     * load existing ontology (TBox or snapshot in previous iteration)
     *
     * @throws OWLOntologyCreationException
     */
    private void loadBootstrapOnto() throws OWLOntologyCreationException {
        if (snp_f.exists()) {
            ont = manager.loadOntologyFromOntologyDocument(snp_f);
        } else {
            File OntoFile = new File(HOME_DIR, "FlightOntology.owl");
            ont = manager.loadOntologyFromOntologyDocument(OntoFile);
        }
    }

    /**
     * save snapshot
     *
     * @throws OWLOntologyStorageException
     */
    void save() throws OWLOntologyStorageException {
        manager.saveOntology(ont, IRI.create(snp_f.toURI()));
    }


    /**
     * get all the individuals
     *
     * @return
     */
    ArrayList<String> getIndividuals() {
        ArrayList<String> I = new ArrayList<>();
        OWLNamedIndividual[] S = ont.individualsInSignature().toArray(OWLNamedIndividual[]::new);
        for (OWLNamedIndividual s : S) {
            I.add(s.toStringID().substring(ontIRI.length()));
        }
        return I;
    }


    /**
     * get entailment closure
     *
     * @return
     */
    ArrayList<String> getEntClosure() {
        ArrayList<String> G = new ArrayList<>();

        OWLReasoner reasoner=new Reasoner.ReasonerFactory().createReasoner(ont);

        OWLNamedIndividual[] S = ont.individualsInSignature().toArray(OWLNamedIndividual[]::new);
        OWLObjectProperty[] P = ont.objectPropertiesInSignature().toArray(OWLObjectProperty[]::new);

        for (OWLNamedIndividual s : S) {
            for (OWLObjectProperty p : P) {
                if (p.getIRI().getFragment().equals("topObjectProperty")){
                    continue;
                }
                NodeSet<OWLNamedIndividual> individualValues = reasoner.getObjectPropertyValues(s, p);
                OWLNamedIndividual[] O = individualValues.entities().toArray(OWLNamedIndividual[]::new);
                if (O.length > 0) {
                    for (OWLNamedIndividual o : O) {
                        G.add(String.format("%s,%s,%s", s.toStringID().substring(ontIRI.length()),
                                p.getIRI().getFragment(), o.getIRI().getFragment()));
                    }
                }
            }
        }

        for (OWLClass c : ont.classesInSignature().toArray(OWLClass[]::new)) {
            NodeSet<OWLNamedIndividual> i_set = reasoner.getInstances(c, false);
            OWLNamedIndividual[] i_arr = i_set.entities().toArray(OWLNamedIndividual[]::new);
            for (OWLNamedIndividual i : i_arr) {
                G.add(String.format("%s,%s", c.getIRI().getFragment(), i.getIRI().getFragment()));
            }
        }

        return G;
    }

}
