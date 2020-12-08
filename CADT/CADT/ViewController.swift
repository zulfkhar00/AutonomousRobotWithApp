//
//  ViewController.swift
//  CADT
//
//  Created by Zulfkhar Maukey on 24/11/2020.
//

import UIKit
import Firebase

class ViewController: UIViewController, UIPickerViewDataSource, UIPickerViewDelegate {
    
    @IBOutlet weak var statusLabel: UILabel!
    @IBOutlet weak var pickerView: UIPickerView!
    
    let objects = ["first_item", "second_item", "third_item"]
    let db = Firestore.firestore()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        pickerView.dataSource = self
        pickerView.delegate = self
        
        db.collection("Actions").document("Main").addSnapshotListener { documentSnapshot, error in
              guard let document = documentSnapshot else {
                print("Error fetching document: \(error!)")
                return
              }
              guard let data = document.data() else {
                print("Document data was empty.")
                return
              }
            self.statusLabel.text = data["status"] as? String
        }
    }

    func numberOfComponents(in pickerView: UIPickerView) -> Int {
        return 1
    }
    
    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        return 3
    }
    
    func pickerView(_ pickerView: UIPickerView, titleForRow row: Int, forComponent component: Int) -> String? {
        return objects[row]
    }
    
    func pickerView(_ pickerView: UIPickerView, didSelectRow row: Int, inComponent component: Int) {
        db.collection("Actions").document("Main").setData(["needed_item": objects[row]], merge: true)
    }

}

