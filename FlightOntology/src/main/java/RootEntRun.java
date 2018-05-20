import org.semanticweb.owlapi.model.OWLOntologyCreationException;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

public class RootEntRun {

    private static String HOME_DIR = "/Users/jiahen/Data/US_flights";
    private static String ontIRI = "http://www.cs.ox.ac.uk/isg/krr/ontologies/FlightOntology-1#";
    private static String SNP = "Snapshots_test";
    private static String ENT = "Entailments";

    public static void main(String args[]) throws OWLOntologyCreationException, IOException {
        if (args != null && args.length > 1) {
            HOME_DIR = args[0];
            SNP = args[1];
        }

        File e_f = new File(HOME_DIR, ENT);
        if (!e_f.exists()) {
            e_f.mkdir();
        }
        ArrayList<String> doms = getDomains();
        for (String dom : doms) {
            System.out.printf("\n Domain: %s \n\n", dom);

            ArrayList<ArrayList<String>> Gs = getEntClosures(dom, e_f.getPath());

            ArrayList<String> class_ents = new ArrayList<>();
            ArrayList<String> role_ents = new ArrayList<>();
            for (ArrayList<String> G : Gs) {
                for (String g : G) {
                    if (g.split(",").length==2 && !class_ents.contains(g)) {
                        class_ents.add(g);
                    }
                    if (g.split(",").length==3 && !role_ents.contains(g)) {
                        role_ents.add(g);
                    }
                }
            }
            File class_ent_f = new File(e_f.getPath(), String.format("%s_class_ents.csv", dom));
            File role_ent_f = new File(e_f.getPath(), String.format("%s_role_ents.csv", dom));
            output_ents(class_ent_f, class_ents);
            output_ents(role_ent_f, role_ents);


            System.out.println("Calculate entailment importance \n");
            HashMap<String, Float> imp = calImportance(Gs);

            System.out.println("Calculate entailment effectiveness \n");
            ArrayList<String> ents = new ArrayList<>();
            ents.addAll(class_ents);
            ents.addAll(role_ents);
            HashMap<String, Float[]> eff = calEffectiveness(Gs, ents);


            File imp_f = new File(e_f.getPath(), String.format("%s_imp.csv", dom));
            FileWriter imp_writer = new FileWriter(imp_f.getPath());
            for (String g : imp.keySet()) {
                imp_writer.write(String.format("%s:%f\n", g, imp.get(g)));
            }
            imp_writer.close();

            File eff_f = new File(e_f.getPath(), String.format("%s_eff.csv", dom));
            FileWriter eff_writer = new FileWriter(eff_f.getPath());
            for (String g : eff.keySet()) {
                Float[] e = eff.get(g);
                eff_writer.write(String.format("%s:%f,%f,%f\n", g, e[0], e[1], e[2]));
            }
        }
    }


    /**
     * Calculate the effectiveness of entailments
     *
     * @param Gs
     */
    private static HashMap<String, Float[]> calEffectiveness(ArrayList<ArrayList<String>> Gs, ArrayList<String> ents) {
        String g_t = "DepDelayed,dep";
        HashMap<String, Integer> co_ex = new HashMap<>();
        HashMap<String, Integer> co_inex = new HashMap<>();

        for (String g : ents) {
            co_ex.put(g, 0);
            co_inex.put(g, 0);
        }

        for (ArrayList<String> G : Gs) {
            for (String g : co_ex.keySet()) {
                if (G.contains(g) && G.contains(g_t)) {
                    co_ex.put(g, co_ex.get(g) + 1);
                }
                if (!G.contains(g) && !G.contains(g_t)) {
                    co_inex.put(g, co_inex.get(g) + 1);
                }
            }
        }

        int n = Gs.size();
        HashMap<String, Float[]> eff = new HashMap<>();
        for (String g : co_ex.keySet()) {
            float e = co_ex.get(g) / (float) n;
            float ie = co_inex.get(g) / (float) n;
            Float[] f = {e, ie, e + ie};
            eff.put(g, f);
        }
        return eff;
    }

    /**
     * calculate the importance of each entailment
     *
     * @param Gs
     */
    private static HashMap<String, Float> calImportance(ArrayList<ArrayList<String>> Gs) {
        HashMap<String, Float> imp = new HashMap<>();
        for (ArrayList<String> G : Gs) {
            for (String g : G) {
                if (!imp.containsKey(g)) {
                    imp.put(g, (float) 1.0);
                } else {
                    imp.put(g, imp.get(g) + (float) 1.0);
                }
            }
        }
        for (String g : imp.keySet()) {
            imp.put(g, imp.get(g) / (float) Gs.size());
        }
        return imp;
    }

    /**
     * get entailments closures
     *
     * @param dom
     * @return
     * @throws OWLOntologyCreationException
     */
    private static ArrayList<ArrayList<String>> getEntClosures(String dom, String e_f) throws OWLOntologyCreationException, IOException {
        File ent_num_f = new File(e_f, String.format("%s_ent_num.csv", dom));
        ArrayList<String> snp_ids = getSnpIDs(dom);
        System.out.println("Snapshot size: " + snp_ids.size());
        ArrayList<ArrayList<String>> Gs = new ArrayList<>();
        FileWriter writer = new FileWriter(ent_num_f.getPath());
        for (int i = 0; i < snp_ids.size(); i++) {
            Snapshot snp = new Snapshot(SNP, dom, snp_ids.get(i), HOME_DIR, ontIRI);
            ArrayList<String> G = snp.getEntClosure();
            Gs.add(G);
            writer.write(String.format("%s,%d\n", snp_ids.get(i), G.size()));
            if (i % 100 == 0) {
                System.out.printf("%d: %s, %d \n", i, snp_ids.get(i), G.size());
            }
        }
        writer.close();
        return Gs;
    }

    private static void output_ents(File f, ArrayList<String> ents) throws IOException {
        FileWriter writer = new FileWriter(f.getPath());
        for (String g : ents) {
            writer.write(String.format("%s\n", g));
        }
        writer.close();
    }

    /**
     * Read snapshot ids
     *
     * @param domain
     * @return
     */
    private static ArrayList<String> getSnpIDs(String domain) {
        File snp_f = new File(HOME_DIR, SNP);
        File dom_f = new File(snp_f.getPath(), domain);
        ArrayList<String> snp_ids = new ArrayList<>();
        for (File f : dom_f.listFiles()) {
            String name = f.getName();
            if (name.endsWith(".owl")) {
                snp_ids.add(name.split(".owl")[0]);
            }
        }
        return snp_ids;
    }

    /**
     * Read domains
     *
     * @return
     */
    private static ArrayList<String> getDomains() {
        File d_file = new File(HOME_DIR, SNP);
        ArrayList<String> doms = new ArrayList<>();
        for (File f : d_file.listFiles()) {
            doms.add(f.getName());
        }
        return doms;
    }
}
