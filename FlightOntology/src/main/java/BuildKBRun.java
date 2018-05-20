import org.semanticweb.owlapi.model.*;

import java.io.*;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;

public class BuildKBRun {

    private static String HOME_DIR = "your_home_dir";
    private static String SNP = "Snapshots";
    private static DataAccess data = null;
    private static String ontIRI = "http://www.cs.ox.ac.uk/isg/krr/ontologies/FlightOntology-1#";


    public static void main(String args[]) throws OWLOntologyCreationException, OWLOntologyStorageException, IOException, SQLException {
        if (args != null && args.length > 0) {
        //System.err.println("Not run it on Mac Laptop!");
            HOME_DIR = args[0];
        }
        System.out.printf("HOME_DIR: %s \n\nLet's start!\n\n\n", HOME_DIR);
        HashMap<String, String[]> apt_nebs = new HashMap<>();
        apt_nebs.put("JFK", new String[]{"LGA", "EWR", "PHL"});
        apt_nebs.put("EWR", new String[]{"LGA", "JFK", "PHL"});
        apt_nebs.put("ORD", new String[]{"MDW", "MKE", "DTW"});
        apt_nebs.put("ATL", new String[]{"CLT", "SAV", "BNA"});
        apt_nebs.put("LAX", new String[]{"BUR", "SNA", "SAN"});
        apt_nebs.put("SFO", new String[]{"OAK", "SJC", "SMF"});
        apt_nebs.put("DFW", new String[]{"OKC", "AUS", "IAh"});
        apt_nebs.put("CLT", new String[]{"ATL", "RDU", "CHS"});
        ArrayList<String> doms = getDomains();
        data = new DataAccess();
        for (String dom : doms) {
            String car = dom.substring(0, 2);
            String ori = dom.substring(3, 6);
            String des = dom.substring(7, 10);
            String CRS_dep_t1 = dom.substring(11, 15);
            String CRS_dep_t2 = dom.substring(16, 20);
            String cut_t = CRS_dep_t1;

            target_dep(dom, car, ori, des, CRS_dep_t1, CRS_dep_t2);

            apt_mete(dom, ori, "ori", cut_t);

            apt_rec(dom, 13, ori, cut_t);

            for (String apt_neb : apt_nebs.get(ori)) {
                apt_rec(dom, 5, apt_neb, cut_t);
            }

            car_rec(dom, 10, car, cut_t);

            car_ori_rec(dom, 5, car, ori, cut_t);

            apt_mete(dom, des, "des", cut_t);
        }
        data.close();
    }


    /**
     * Target Departure (Y)
     */
    private static void target_dep(String dom, String car, String ori, String des, String CRS_dep_t1, String CRS_dep_t2)
            throws SQLException, OWLOntologyCreationException, OWLOntologyStorageException {
        System.out.printf("\n\n domain: %s \nTarget departure related axioms\n\n", dom);
        System.out.printf(" ----- %s, Y: access data ---- \n", dom);
        ArrayList<HashMap<String, String>> targets = new ArrayList<>();
        for (int y = 2010; y <= 2017; y++) {
            targets.addAll(data.getTargetDep(y, car, ori, des, CRS_dep_t1, CRS_dep_t2));
        }
        System.out.printf(" ----- %s, Y: add axioms ---- \n", dom);
        for (HashMap<String, String> tar : targets) {
            String snp_id = String.format("%s_%s_%s", tar.get("FlightDate"), tar.get("Carrier"), tar.get("FlightNum"));
            Snapshot snp = new Snapshot(SNP, dom, snp_id, HOME_DIR, ontIRI);
            snp.addTarget(car, ori, des, tar);
            snp.save();
            //System.out.printf("    %s done\n", snp_id);
        }
    }

    /**
     * Airport Mete (X1, X7)
     *
     * @param dom
     * @param apt
     * @param ori_or_des
     * @param CRS_dep_t1
     * @throws SQLException
     * @throws OWLOntologyCreationException
     * @throws OWLOntologyStorageException
     */
    private static void apt_mete(String dom, String apt, String ori_or_des, String CRS_dep_t1)
            throws SQLException, OWLOntologyCreationException, OWLOntologyStorageException {
        System.out.printf("\n\n domain: %s \n%s mete related axioms\n\n", dom, ori_or_des);
        System.out.printf(" ----- %s, X1: access data ---- \n", dom);
        HashMap<String, HashMap<String, String>> d_met = data.getMete(apt, CRS_dep_t1);
        System.out.printf(" ----- %s, X1: add axioms ---- \n", dom);
        for (String snp_id : getSnpIDs(dom)) {
            String k = snp_id.substring(0, 10);
            if (d_met.containsKey(k)) {
                Snapshot snp = new Snapshot(SNP, dom, snp_id, HOME_DIR, ontIRI);
                snp.addMete(ori_or_des, d_met.get(k));
                snp.save();
            }
            //System.out.printf("    %s done\n", snp_id);
        }
    }

    /**
     * recent N1 (<= 13 for origin, <=5 for neighbour) flights at an airport (X2, X5)
     *
     * @param dom
     * @param N
     * @param apt
     * @param cut_t
     */
    private static void apt_rec(String dom, int N, String apt, String cut_t) throws SQLException, OWLOntologyStorageException, OWLOntologyCreationException {
        System.out.printf("\n\n domain: %s \naxioms of recent %d departures at %s \n\n", dom, N, apt);
        System.out.printf(" ----- %s, X2, X5: access data ---- \n", dom);
        HashMap<String, ArrayList<HashMap<String, String>>> d_dep = new HashMap<>();
        for (int y = 2010; y <= 2017; y++) {
            d_dep.putAll(data.getAptRec(y, N, apt, cut_t));
        }
        System.out.printf(" ----- %s, X2, X5: add axioms ---- \n", dom);
        for (String snp_id : getSnpIDs(dom)) {
            String k = snp_id.substring(0, 10);
            if (d_dep.containsKey(k)) {
                Snapshot snp = new Snapshot(SNP, dom, snp_id, HOME_DIR, ontIRI);
                snp.addAptDep(apt, d_dep.get(k));
                snp.save();
            }
            //System.out.printf("    %s done\n", snp_id);
        }
    }


    /**
     * recent N2 <= 5 flights of the carrier at the origin (X3)
     *
     * @param dom
     * @param N
     * @param car
     * @param ori
     * @param cut_t
     */
    private static void car_ori_rec(String dom, int N, String car, String ori, String cut_t) throws SQLException, OWLOntologyStorageException, OWLOntologyCreationException {
        System.out.printf("\n\n domain: %s \naxioms of recent 5 flights of %s at %s \n\n", dom, car, ori);
        System.out.printf(" ----- %s, X3: access data ---- \n", dom);
        HashMap<String, ArrayList<HashMap<String, String>>> d_dep = new HashMap<>();
        for (int y = 2010; y <= 2017; y++) {
            d_dep.putAll(data.getCarAptRec(y, N, car, ori, cut_t));
        }
        System.out.printf(" ----- %s, X3: add axioms ---- \n", dom);
        for (String snp_id : getSnpIDs(dom)) {
            String k = snp_id.substring(0, 10);
            if (d_dep.containsKey(k)) {
                Snapshot snp = new Snapshot(SNP, dom, snp_id, HOME_DIR, ontIRI);
                snp.addCarOriDep(car, d_dep.get(k));
                snp.save();
            }
            //System.out.printf("    %s done\n", snp_id);
        }
    }


    /**
     * recent N3 <= 13 flights of the carrier (X4)
     *
     * @param dom
     * @param N
     * @param car
     * @param cut_t
     */
    private static void car_rec(String dom, int N, String car, String cut_t) throws SQLException, OWLOntologyStorageException, OWLOntologyCreationException {
        System.out.printf("\n\n domain: %s \naxioms of recent 5 flights of %s \n\n", dom, car);
        System.out.printf(" ----- %s, X4: access data ---- \n", dom);
        HashMap<String, ArrayList<HashMap<String, String>>> d_dep = new HashMap<>();
        for (int y = 2010; y <= 2017; y++) {
            d_dep.putAll(data.getCarRec(y, N, car, cut_t));
        }
        System.out.printf(" ----- %s, X4: add axioms ---- \n", dom);
        for (String snp_id : getSnpIDs(dom)) {
            String k = snp_id.substring(0, 10);
            if (d_dep.containsKey(k)) {
                Snapshot snp = new Snapshot(SNP, dom, snp_id, HOME_DIR, ontIRI);
                snp.addCarDep(d_dep.get(k));
                snp.save();
            }
        }
    }

    /**
     * Read domains
     *
     * @return
     */
    private static ArrayList<String> getDomains() {
        File d_file = new File(HOME_DIR, "Sample_Ori");
        ArrayList<String> doms = new ArrayList<>();
        for (File f : d_file.listFiles()) {
            doms.add(f.getName());
        }
        return doms;
    }

    /**
     * Read snapshot ids
     *
     * @param domain
     * @return
     */
    private static ArrayList<String> getSnpIDs(String domain) {
        File snp_f = new File(HOME_DIR, "Snapshots");
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

}
