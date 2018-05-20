import org.apache.jena.query.QueryExecution;
import org.apache.jena.query.QueryExecutionFactory;
import org.apache.jena.query.QuerySolution;
import org.apache.jena.query.ResultSet;
import org.apache.jena.sparql.engine.http.QueryEngineHTTP;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;

public class XKnowRun {
    private static String HOME_DIR = "your_home_dir/Onto/Entailments";

    public static void main(String args[]) throws IOException {
        for (String dom: read_doms()) {
            System.out.println("Domain: " + dom + "\n");
            ArrayList<String> x_axioms = new ArrayList<>();
            ArrayList<String> root_inds = read_root_ind(dom);
            HashMap<String, ArrayList<String>> ind_cls = read_class(root_inds, dom);
            for (String ind : root_inds) {

                if (ind_cls.get(ind).contains("Carrier")) {
                    //System.out.println("Carrier: " + ind);
                    for (String axiom : import_know_carrier(ind)) {
                        if (!x_axioms.contains(axiom)) {
                            x_axioms.add(axiom);
                        }
                    }
                }

                if (ind_cls.get(ind).contains("Airport")) {
                    //System.out.println("Airport: " + ind);
                    for (String axiom: import_know_airport(ind)){
                        if (!x_axioms.contains(axiom)) {
                            x_axioms.add(axiom);
                        }
                    }
                } else if (ind_cls.get(ind).contains("City")) {
                    //System.out.println("City: " + ind);
                    for (String axiom: import_know_city(ind)){
                        if (!x_axioms.contains(axiom)) {
                            x_axioms.add(axiom);
                        }
                    }
                } else if (ind_cls.get(ind).contains("State")) {
                    //System.out.println("State: " + ind);
                    for (String axiom : import_know_state(ind)){
                        if (!x_axioms.contains(axiom)) {
                            x_axioms.add(axiom);
                        }

                    }
                }
            }

            write_axioms(x_axioms, dom);
        }
    }

    /**
     * import knowledge of carrier individual
     * @param ind
     * @return
     */
    private static ArrayList<String> import_know_carrier(String ind) {
        ArrayList<String> axioms = new ArrayList<>();
        HashMap<String, String> full_name = new HashMap<>();
        full_name.put("VX", "Virgin America");
        full_name.put("WN", "Southwest Airlines");
        full_name.put("AA", "American Airlines");
        full_name.put("UA", "United Airlines");
        full_name.put("DL", "Delta Air Lines");
        full_name.put("CO", "Continental Airlines");
        full_name.put("NK", "Spirit Airlines");
        full_name.put("B6", "JetBlue");
        full_name.put("OO", "SkyWest Airlines");
        full_name.put("MU", "China Eastern Airlines");
        full_name.put("EM", "Empire Airlines");
        String[] d_atts = {"fleetSize", "revenue", "assets", "numberOfEmployees"};
        String [] p_atts = {"hubAirport", "headquarter"};
        if (full_name.containsKey(ind)) {
            String query = String.format("SELECT ?p ?o WHERE { <http://dbpedia.org/resource/%s> ?p ?o.}",
                    full_name.get(ind).replace(" ", "_"));
            QueryExecution qexec = QueryExecutionFactory.sparqlService("http://dbpedia.org/sparql", query);
            ((QueryEngineHTTP) qexec).addParam("timeout", "10000");
            ResultSet rs = qexec.execSelect();
            while (rs.hasNext()) {
                QuerySolution row = rs.next();
                axioms.addAll(extractAxioms(ind, row, d_atts, p_atts));
            }
        }
        return axioms;

    }

    private static ArrayList<String> import_know_city(String ind) {
        String[] d_atts = {"populationTotal", "lat", "long"};
        String[] p_atts = {};
        ArrayList<String> axioms = new ArrayList<>();
        String query = String.format("SELECT ?p ?o WHERE { <http://dbpedia.org/resource/%s> ?p ?o.}", ind);
        QueryExecution qexec = QueryExecutionFactory.sparqlService("http://dbpedia.org/sparql", query);
        ((QueryEngineHTTP) qexec).addParam("timeout", "10000");
        ResultSet rs = qexec.execSelect();
        while (rs.hasNext()) {
            QuerySolution row = rs.next();
            axioms.addAll(extractAxioms(ind, row, d_atts, p_atts));
        }
        return axioms;
    }

    private static ArrayList<String> import_know_state(String ind) {
        String[] d_atts = {"areaTotal", "lat", "long"};
        String[] p_atts = {"east","west"};
        ArrayList<String> axioms = new ArrayList<>();
        String query = String.format("SELECT ?s ?p ?o WHERE { ?s <http://dbpedia.org/property/postalabbreviation> " +
                "'%S'^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#langString>. ?s ?p ?o}", ind.substring(2,4));
        QueryExecution qexec = QueryExecutionFactory.sparqlService("http://dbpedia.org/sparql", query);
        ((QueryEngineHTTP) qexec).addParam("timeout", "10000");
        ResultSet rs = qexec.execSelect();
        while (rs.hasNext()) {
            QuerySolution row = rs.next();
            axioms.addAll(extractAxioms(ind, row, d_atts, p_atts));
        }
        return axioms;
    }

    private static ArrayList<String> import_know_airport(String ind) {
        String[] d_atts = {"elevation", "lat", "long"};
        String[] p_atts = {"city", "location"};
        ArrayList<String> axioms = new ArrayList<>();
        String query = String.format("SELECT ?p ?o WHERE { ?s <http://dbpedia.org/ontology/iataLocationIdentifier> 'JFK'. " +
                "?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/Airport>. ?s ?p ?o.}", ind);
        QueryExecution qexec = QueryExecutionFactory.sparqlService("http://dbpedia.org/sparql", query);
        ((QueryEngineHTTP) qexec).addParam("timeout", "10000");
        ResultSet rs = qexec.execSelect();
        while (rs.hasNext()) {
            QuerySolution row = rs.next();
            axioms.addAll(extractAxioms(ind, row, d_atts, p_atts));

        }
        return axioms;
    }


    private static ArrayList<String> extractAxioms(String ind, QuerySolution row, String [] d_atts, String [] p_atts){
        String p = row.get("p").toString();
        String o = row.get("o").toString();
        ArrayList<String> axioms  = new ArrayList<>();
        if (p.endsWith("label") && o.endsWith("@en")) {
            axioms.add(String.format("%s,<%s>,<%s>", ind, p, o));
        }
        for (String att : p_atts) {
            if (p.endsWith(att)) {
                axioms.add(String.format("%s,<%s>,<%s>", ind,p, o));
            }
        }
        for (String att : d_atts) {
            if (p.equals(att)) {
                axioms.add(String.format("%s,<%s>,<%s>", ind, p, o));
            }
        }
        return axioms;
    }

    /**
     * get the classes of an individual
     *
     * @param root_inds
     * @return
     * @throws IOException
     */
    private static HashMap<String, ArrayList<String>> read_class(ArrayList<String> root_inds, String DOM) throws IOException {
        HashMap<String, ArrayList<String>> ind_cls = new HashMap<>();
        for (String ind : root_inds) {
            ArrayList<String> cls = new ArrayList<>();
            ind_cls.put(ind, cls);
        }
        File ind_cls_f = new File(HOME_DIR, String.format("%s_class_ents.csv", DOM));
        InputStreamReader read = new InputStreamReader(new FileInputStream(ind_cls_f));
        BufferedReader bufferedReader = new BufferedReader(read);
        String line;
        while ((line = bufferedReader.readLine()) != null) {
            String[] tmp = line.trim().split(",");
            String i = tmp[1];
            String c = tmp[0];
            if (ind_cls.containsKey(i)) {
                ind_cls.get(i).add(c);
            }
        }
        bufferedReader.close();
        read.close();
        return ind_cls;
    }

    /**
     * read root individuals
     *
     * @return
     * @throws IOException
     */
    private static ArrayList<String> read_root_ind(String DOM) throws IOException {
        ArrayList<String> root_inds = new ArrayList<>();
        File root_ind_f = new File(HOME_DIR, String.format("%s_root_ind.csv", DOM));
        InputStreamReader read = new InputStreamReader(new FileInputStream(root_ind_f));
        BufferedReader bufferedReader = new BufferedReader(read);
        String line;
        while ((line = bufferedReader.readLine()) != null) {
            root_inds.add(line.trim());
        }
        bufferedReader.close();
        read.close();
        return root_inds;
    }


    /**
     * read domains
     * @return
     */
    private static ArrayList<String> read_doms(){
        ArrayList<String> doms = new ArrayList<>();
        File d = new File(HOME_DIR);
        for (File f: d.listFiles()){
            String dom = f.getName().substring(0, 20);
            if (!doms.contains(dom)){
                doms.add(dom);
            }
        }
        return doms;
    }

    /**
     * save X axioms
     * @param axioms
     * @param dom
     * @throws IOException
     */
    private static void write_axioms(ArrayList<String> axioms, String dom) throws IOException {
        File f = new File(HOME_DIR, String.format("%s_x_axioms.csv", dom));
        FileWriter writer = new FileWriter(f.getPath());
        for (String a : axioms) {
            writer.write(String.format("%s\n", a));
        }
        writer.close();
    }
}
